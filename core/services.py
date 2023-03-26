import calendar
import decimal
from tzlocal import get_localzone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Sum, Case, When, F, DecimalField
from django.db.models.functions import TruncDate, Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from accounts.models import Account
from products.models import PointValue
from core.enums import Settings, WalletType, ActivityStatus, ActivityType
from core.models import Activity, MembershipLevel, Setting


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def get_settings():
    return Setting.objects.all()


def get_setting(property):
    return Setting.objects.get(property=property).value


def create_activity(
    account=None,
    activity_type=None,
    activity_amount=None,
    status=None,
    wallet=None,
    membership_level=None,
    product_variant=None,
    content_type=None,
    object_id=None,
    user=None,
):
    if user.is_authenticated:
        return Activity.objects.create(
            account=account,
            activity_type=activity_type,
            activity_amount=activity_amount,
            status=status,
            wallet=wallet,
            membership_level=membership_level,
            product_variant=product_variant,
            content_type=content_type,
            object_id=object_id,
            created_by=user,
        )
    else:
        return Activity.objects.create(
            account=account,
            activity_type=activity_type,
            activity_amount=activity_amount,
            status=status,
            wallet=wallet,
            membership_level=membership_level,
            product_variant=product_variant,
            content_type=content_type,
            object_id=object_id,
        )


def compute_minimum_conversion_amount(amount):
    minimum_conversion_amount = int(get_setting(property=Settings.MINIMUM_CONVERSTION_AMOUNT))
    if minimum_conversion_amount:
        return amount >= minimum_conversion_amount, minimum_conversion_amount
    return False, 0


def compute_conversion_amount(amount):
    conversion_rate = int(get_setting(property=Settings.POINT_CONVERSION_RATE))
    if conversion_rate:
        return amount * conversion_rate
    return 0


def process_point_conversion(request):
    total_converted_points = 0
    try:
        for activity in request.data.get("activities"):
            current_points = decimal.Decimal(activity.get("current_points"))
            membership_level = activity.get("membership_level")

            remaining_points = (
                Activity.objects.filter(account__user=request.user.pk)
                .values("activity_type")
                .annotate(
                    activity_total=Case(
                        When(
                            Q(activity_type=ActivityType.POINT_CONVERSION) & Q(membership_level=membership_level),
                            then=0 - (Sum(F("activity_amount"))),
                        ),
                        When(
                            ~Q(activity_type=ActivityType.POINT_CONVERSION),
                            then=Sum(F("activity_amount")),
                        ),
                    ),
                )
                .aggregate(total=Coalesce(Sum("activity_total"), 0, output_field=DecimalField()))
                .get("total")
            )

            if remaining_points - current_points > 0:
                can_convert, minimum_conversion_amount = compute_minimum_conversion_amount(current_points)
                if can_convert:
                    converted_amount = compute_conversion_amount(current_points)
                    create_point_conversion_activity(
                        request, converted_amount=converted_amount, membership_level_id=membership_level
                    )
                    total_converted_points += converted_amount
        else:
            create_currency_conversion_activity(request, total_converted_points=total_converted_points)
            return True
    except Exception as e:
        print(e)
        return False


def create_point_conversion_activity(request, converted_amount, membership_level_id):
    account = get_object_or_404(Account, account_id=request.data.get("account_id"))
    membership_level_id = get_object_or_404(MembershipLevel, id=membership_level_id)

    return create_activity(
        account=account,
        activity_type=ActivityType.POINT_CONVERSION,
        activity_amount=-abs(converted_amount),
        status=ActivityStatus.DONE,
        wallet=WalletType.PV_WALLET,
        membership_level=membership_level_id,
        user=request.user,
    )


def create_currency_conversion_activity(request, total_converted_points):
    account = get_object_or_404(Account, account_id=request.data.get("account_id"))

    return create_activity(
        account=account,
        activity_type=ActivityType.POINT_CONVERSION,
        activity_amount=total_converted_points,
        status=ActivityStatus.DONE,
        wallet=WalletType.M_WALLET,
        user=request.user,
    )


def get_wallet_cashout_schedule():
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    calendar.setfirstweekday(calendar.SUNDAY)
    data = []
    for wallet in [
        WalletType.M_WALLET,
    ]:
        property = "%s%s" % (wallet, "_CASHOUT_DAY")
        if property:
            day = int(get_setting(property=property))
            data.append({wallet: " is open during %s" % days[day]})
    else:
        return data


def get_wallet_can_cashout(wallet):
    if wallet == WalletType.M_WALLET:
        property = "%s%s" % (wallet, "_CASHOUT_DAY")
        if property:
            day = int(get_setting(property=property))
            if day == timezone.localtime().isoweekday():
                return True
            else:
                has_override = "%s%s" % (wallet, "_CASHOUT_OVERRIDE")
                if bool(int(get_setting(property=has_override))):
                    return True
                else:
                    return False


def check_if_has_cashout_today(request):
    wallet = request.data.get("wallet")
    if wallet:
        local_tz = get_localzone()
        return Activity.objects.annotate(modified_local_tz=TruncDate("modified", tzinfo=local_tz)).filter(
            account__user=request.user.pk,
            activity_type=ActivityType.CASHOUT,
            wallet=wallet,
            modified_local_tz=timezone.localtime().date(),
        )
    return True


def check_if_has_pending_cashout(request):
    wallet = request.data.get("wallet")
    if wallet:
        return Activity.objects.filter(
            Q(activity_type=ActivityType.CASHOUT)
            & Q(Q(status=ActivityStatus.REQUESTED) | Q(status=ActivityStatus.APPROVED)),
            account__user=request.user.pk,
            wallet=wallet,
        )
    return True


def get_cashout_processing_fee_percentage():
    cashout_processing_fee_percentage = decimal.Decimal(get_setting(Settings.CASHOUT_PROCESSING_FEE_PERCENTAGE))
    return cashout_processing_fee_percentage


def compute_cashout_total(request):
    data = {}
    cashout_processing_fee_percentage = get_cashout_processing_fee_percentage()
    total_cashout = decimal.Decimal(request.data["amount"]) * ((100 - cashout_processing_fee_percentage) / 100)

    if total_cashout and cashout_processing_fee_percentage:
        data["activity_admin_fee"] = cashout_processing_fee_percentage
        data["activity_total_amount"] = total_cashout
        return data, "Valid"

    return data, "Unable to retrieve Total Cashout Amount"


def compute_minimum_cashout_amount(amount, wallet):
    if wallet == WalletType.M_WALLET:
        property = "%s%s" % (wallet, "_MINIMUM_CASHOUT_AMOUNT")

        if property:
            minimum_cashout_amount = int(get_setting(property=property))
            return amount >= minimum_cashout_amount, minimum_cashout_amount
    return False, 0


def process_create_cashout_request(request):
    from accounts.models import Account, CashoutMethod
    from accounts.services import create_new_cashout_method

    content_type = ContentType.objects.get(model="cashoutmethod")
    account = get_object_or_404(Account, account_id=request.data["account_id"])

    if account:
        data = {
            "account": account.pk,
            "activity_type": ActivityType.CASHOUT,
            "activity_amount": request.data.get("activity_amount"),
            "wallet": request.data.get("wallet"),
            "status": ActivityStatus.REQUESTED,
            "note": request.data.get("note"),
            "details": [
                {
                    "action": "Cashout Requested",
                    "created_by": request.user.pk,
                }
            ],
            "created_by": request.user.pk,
            "content_type": content_type.pk,
            "object_id": "",
        }

        if isinstance(request.data.get("cashout_method").get("cashout_method_id"), str) and request.data.get(
            "cashout_method"
        ).get("cashout_method_id"):
            cashout_method = get_object_or_404(
                CashoutMethod, id=request.data.get("cashout_method").get("cashout_method_id")
            )
            data["object_id"] = cashout_method.pk
        elif isinstance(request.data.get("cashout_method"), dict):
            cashout_method = create_new_cashout_method(request, account)
            data["object_id"] = cashout_method.pk

        return data


def process_update_cashout_status(request):
    cashout = Activity.objects.get(id=request.data["activity_number"].lstrip("0"))
    data = {}
    details = []
    if cashout:
        if request.data["status"] == ActivityStatus.APPROVED:
            details.append({"action": "Cashout Approved", "created_by": request.user.pk})
        elif request.data["status"] == ActivityStatus.RELEASED:
            details.append({"action": "Cashout Released", "created_by": request.user.pk})
        elif request.data["status"] == ActivityStatus.DENIED:
            details.append({"action": "Cashout Denied", "created_by": request.user.pk})

        data["details"] = details
        data["status"] = request.data["status"]

        return cashout, data


def convert_point_value_queryset_to_map(point_values):
    data = {}
    for point_value in point_values:
        data[point_value.membership_level.level] = {
            "membership_level": point_value.membership_level,
            "name": point_value.membership_level.name,
            "level": point_value.membership_level.level,
            "point_value": point_value.point_value,
        }

    return data


def create_referral_link_usage_activity(request, order, account, point_value, membership_level, product_variant):
    content_type = ContentType.objects.get(model="order")

    return create_activity(
        account=account,
        activity_type=ActivityType.REFERRAL_LINK_USAGE,
        activity_amount=point_value,
        status=ActivityStatus.DONE,
        wallet=WalletType.PV_WALLET,
        membership_level=membership_level,
        product_variant=product_variant,
        content_type=content_type,
        object_id=order.pk,
        user=request.user,
    )


def create_purchase_activity(request, order):
    content_type = ContentType.objects.get(model="order")
    if order.account:
        return create_activity(
            account=order.account,
            activity_type=ActivityType.ENTRY,
            activity_amount=order.total_amount,
            status=ActivityStatus.DONE,
            wallet=WalletType.C_WALLET,
            content_type=content_type,
            object_id=order.pk,
            user=request.user,
        )

    return create_activity(
        activity_type=ActivityType.ENTRY,
        activity_amount=order.total_amount,
        status=ActivityStatus.DONE,
        wallet=WalletType.C_WALLET,
        content_type=content_type,
        object_id=order.pk,
        user=request.user,
    )


def create_payout_activity(request, updated_cashout):
    if updated_cashout:
        content_type = ContentType.objects.get(model="activity")
        total_tax = (100 - get_cashout_processing_fee_percentage()) / 100

        return create_activity(
            account=updated_cashout.account,
            activity_type=ActivityType.PAYOUT,
            activity_amount=updated_cashout.activity_amount * total_tax,
            status=ActivityStatus.DONE,
            wallet=WalletType.C_WALLET,
            content_type=content_type,
            object_id=updated_cashout.pk,
            user=request.user,
        )


def create_company_earning_activity(request, updated_cashout):
    if updated_cashout:
        content_type = ContentType.objects.get(model="activity")
        total_tax_earning = get_cashout_processing_fee_percentage() / 100

        return create_activity(
            account=updated_cashout.account,
            activity_type=ActivityType.CASHOUT_PROCESSING_FEE,
            activity_amount=updated_cashout.activity_amount * total_tax_earning,
            status=ActivityStatus.DONE,
            wallet=WalletType.C_WALLET,
            content_type=content_type,
            object_id=updated_cashout.pk,
            user=request.user,
        )


def comp_plan(request, order):
    four_level_referrers = order.promo_code.account.get_four_level_referrers()
    for referrer in four_level_referrers:
        level = referrer["level"]
        account = referrer["account"]
        for detail in order.details.all():
            quantity = detail.quantity
            point_values = convert_point_value_queryset_to_map(detail.product_variant.point_values.all())
            for _ in range(quantity):
                create_referral_link_usage_activity(
                    request,
                    order,
                    account,
                    point_values[level]["point_value"],
                    point_values[level]["membership_level"],
                    detail.product_variant,
                )

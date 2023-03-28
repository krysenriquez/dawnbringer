from django.db.models import Case, Value, When, Sum, F, Q, DecimalField, Count, Prefetch
from django.db.models.functions import Coalesce
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from core.enums import ActivityStatus, Settings, ActivityType, WalletType
from core.models import Setting, MembershipLevel, Activity, CashoutMethods
from core.serializers import (
    CreateUpdateActivitySerializer,
    SettingsSerializer,
    MembershipLevelsSerializer,
    CashoutMethodsListSerializer,
    ActivitiesSerializer,
    ActivityCashoutListSerializer,
    ActivityCashoutInfoSerializer,
)
from core.services import (
    check_if_has_cashout_today,
    check_if_has_pending_cashout,
    compute_cashout_total,
    compute_conversion_amount,
    compute_minimum_cashout_amount,
    compute_minimum_conversion_amount,
    create_company_earning_activity,
    create_payout_activity,
    get_cashout_processing_fee_percentage,
    get_setting,
    get_wallet_can_cashout,
    get_wallet_cashout_schedule,
    process_create_cashout_request,
    process_point_conversion,
    process_update_cashout_status,
)
from users.models import User
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser, IsMemberUser
from orders.models import Order


class SettingsListViewSet(ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Setting.objects.all().order_by("-property")


class SettingInfoViewSet(ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        property = self.request.query_params.get("property", None)
        if property:
            return Setting.objects.filter(property=property).order_by("-property")


class MembershipLevelsViewSet(ModelViewSet):
    queryset = MembershipLevel.objects.all()
    serializer_class = MembershipLevelsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return MembershipLevel.objects.all().order_by("level")


class CashoutMethodsListViewSet(ModelViewSet):
    queryset = CashoutMethods.objects.all()
    serializer_class = CashoutMethodsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return CashoutMethods.objects.exclude(is_deleted=True).exclude(is_disabled=True).all().order_by("method_name")


class ActivitiesListMemberViewSet(ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitiesSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Activity.objects.filter(account__user=self.request.user).order_by("-id")


class CashoutAdminListViewSet(ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivityCashoutListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Activity.objects.filter(activity_type=ActivityType.CASHOUT).exclude(is_deleted=True)

        return queryset


class CashoutAdminInfoViewSet(ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivityCashoutInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        activity_number = self.request.query_params.get("activity_number", None)
        if activity_number is not None:
            queryset = Activity.objects.filter(activity_type=ActivityType.CASHOUT, id=activity_number).exclude(
                is_deleted=True
            )

            return queryset


class CashoutMemberInfoViewSet(ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivityCashoutInfoSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        activity_number = self.request.query_params.get("activity_number", None)
        if activity_number is not None:
            return Activity.objects.filter(
                activity_type=ActivityType.CASHOUT, account__user=self.request.user, id=activity_number
            ).exclude(is_deleted=True)


class CashoutMemberListViewSet(ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivityCashoutListSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Activity.objects.filter(activity_type=ActivityType.CASHOUT, account__user=self.request.user).exclude(
            is_deleted=True
        )


class GetMembershipLevelPointsAdminView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        account_id = request.data.get("account_id")
        if account_id:
            membership_level_points = (
                MembershipLevel.objects.prefetch_related(
                    Prefetch("activities", queryset=Activity.objects.filter(account__account_id=account_id))
                )
                .annotate(
                    total=Coalesce(
                        Sum("activities__activity_amount", filter=Q(activities__account__account_id=account_id)),
                        0,
                        output_field=DecimalField(),
                    )
                )
                .values("name", "total")
                .order_by("id")
            )

            member_wallet_total = (
                (
                    Activity.objects.filter(wallet=WalletType.M_WALLET, account__account_id=account_id)
                    .values("activity_type")
                    .annotate(
                        activity_total=Case(
                            When(
                                Q(activity_type=ActivityType.CASHOUT) & ~Q(status=ActivityStatus.DENIED),
                                then=0 - (Sum(F("activity_amount"))),
                            ),
                            When(
                                ~Q(activity_type=ActivityType.CASHOUT),
                                then=Sum(F("activity_amount")),
                            ),
                        ),
                    )
                    .order_by("-activity_total")
                )
                .aggregate(total=Coalesce(Sum("activity_total"), 0, output_field=DecimalField()))
                .get("total")
            )

            member_wallet_total_cashout = (
                (
                    Activity.objects.filter(wallet=WalletType.M_WALLET, account__account_id=account_id)
                    .values("activity_type")
                    .annotate(
                        activity_total=Case(
                            When(
                                Q(activity_type=ActivityType.CASHOUT),
                                then=Sum(F("activity_amount")),
                            ),
                        ),
                    )
                    .order_by("-activity_total")
                )
                .aggregate(total=Coalesce(Sum("activity_total"), 0, output_field=DecimalField()))
                .get("total")
            )

            return Response(
                data={
                    "membership_level_points": membership_level_points,
                    "member_wallet": member_wallet_total,
                    "cashout": member_wallet_total_cashout,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Account does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )


class GetMembershipLevelPointsMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        membership_level_points = (
            MembershipLevel.objects.prefetch_related(
                Prefetch("activities", queryset=Activity.objects.filter(account__user=self.request.user))
            )
            .annotate(
                total=Coalesce(
                    Sum("activities__activity_amount", filter=Q(activities__account__user=self.request.user)),
                    0,
                    output_field=DecimalField(),
                )
            )
            .values("name", "total")
            .order_by("id")
        )

        member_wallet_total = (
            (
                Activity.objects.filter(wallet=WalletType.M_WALLET, account__user=self.request.user)
                .values("activity_type")
                .annotate(
                    activity_total=Case(
                        When(
                            Q(activity_type=ActivityType.CASHOUT) & ~Q(status=ActivityStatus.DENIED),
                            then=0 - (Sum(F("activity_amount"))),
                        ),
                        When(
                            ~Q(activity_type=ActivityType.CASHOUT),
                            then=Sum(F("activity_amount")),
                        ),
                    ),
                )
                .order_by("-activity_total")
            )
            .aggregate(total=Coalesce(Sum("activity_total"), 0, output_field=DecimalField()))
            .get("total")
        )

        member_wallet_total_cashout = (
            (
                Activity.objects.filter(wallet=WalletType.M_WALLET, account__user=self.request.user)
                .values("activity_type")
                .annotate(
                    activity_total=Case(
                        When(
                            Q(activity_type=ActivityType.CASHOUT),
                            then=Sum(F("activity_amount")),
                        ),
                    ),
                )
                .order_by("-activity_total")
            )
            .aggregate(total=Coalesce(Sum("activity_total"), 0, output_field=DecimalField()))
            .get("total")
        )

        return Response(
            data={
                "membership_level_points": membership_level_points,
                "member_wallet": member_wallet_total,
                "cashout": member_wallet_total_cashout,
            },
            status=status.HTTP_200_OK,
        )


class GetPointConversionRateView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        conversion_rate = get_setting(Settings.POINT_CONVERSION_RATE)
        if conversion_rate:
            return Response(
                data={"conversion_rate": conversion_rate},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Conversion Rate"},
            status=status.HTTP_404_NOT_FOUND,
        )


class GetMaxPointConversionAmountView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        membership_level = request.data.get("membership_level")
        amount = request.data.get("amount")
        if amount is not None and membership_level is not None:
            activities = (
                Activity.objects.filter(account__user=self.request.user.pk, membership_level=membership_level)
                .values("activity_type")
                .annotate(
                    running_total=Case(
                        When(
                            ~Q(activity_type=ActivityType.POINT_CONVERSION),
                            then=Sum(F("activity_amount")),
                        ),
                    ),
                    activity_total=Case(
                        When(
                            Q(activity_type=ActivityType.POINT_CONVERSION),
                            then=0 - (Sum(F("activity_amount"))),
                        ),
                        When(
                            ~Q(activity_type=ActivityType.POINT_CONVERSION),
                            then=Sum(F("activity_amount")),
                        ),
                    ),
                    conversion_total=Case(
                        When(
                            Q(activity_type=ActivityType.POINT_CONVERSION),
                            then=0 - (Sum(F("activity_amount"))),
                        ),
                    ),
                )
                .order_by("-activity_total")
            )

            remaining_points = activities.aggregate(
                total=Coalesce(Sum("activity_total"), 0, output_field=DecimalField())
            ).get("total")

            if remaining_points - int(amount) >= 0:
                can_convert, minimum_conversion_amount = compute_minimum_conversion_amount(amount)
                if can_convert:
                    converted_amount = compute_conversion_amount(amount)
                    return Response(
                        data={"detail": "Conversion Available", "converted_amount": converted_amount},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    data={"detail": "Minimum amount of " + str(minimum_conversion_amount) + " Points"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            else:
                return Response(
                    data={"detail": "Conversion exceeds Earned Points"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                data={"detail": "No Current Points for Conversion"},
                status=status.HTTP_403_FORBIDDEN,
            )


class CreateConversionView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        is_converted = process_point_conversion(request)
        if is_converted:
            return Response(
                data={"detail": "Points Converted"},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to convert points"},
            status=status.HTTP_404_NOT_FOUND,
        )


class UpdateSettingsView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        settings = request.data
        instances = []
        for setting in settings:
            obj = Setting.objects.get(property=setting["property"])
            if obj:
                obj.property = setting["property"]
                obj.value = setting["value"]
                obj.save()
                instances.append(obj)

        serializer = SettingsSerializer(instances, many=True)
        if serializer:
            return Response(data={"detail": "System Settings Updated."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"detail": "Unable to create Update System Settings."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateMembershipLevelsView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        membership_levels = request.data
        instances = []
        for membership_level in membership_levels:
            obj = MembershipLevel.objects.get(property=membership_level["name"])
            if obj:
                obj.name = membership_level["name"]
                obj.level = membership_level["level"]
                obj.save()
                instances.append(obj)

        serializer = MembershipLevelsSerializer(instances, many=True)
        if serializer:
            return Response(data={"detail": "Membership Levels Updated."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"detail": "Unable to create Update Membership Levels."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Cashouts
class GetWalletCanCashoutView(views.APIView):

    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        if get_wallet_can_cashout(request.data.get("wallet")):
            no_cashout_today = not check_if_has_cashout_today(request)
            if no_cashout_today:
                has_no_pending_cashout = not check_if_has_pending_cashout(request)
                if has_no_pending_cashout:
                    return Response(
                        data={"detail": "Cashout Available"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        data={"detail": "Pending Cashout request existing for Wallet."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                return Response(
                    data={"detail": "Max Cashout reached today."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                data={"detail": "Cashout currently unavailable."},
                status=status.HTTP_403_FORBIDDEN,
            )


class GetWalletScheduleView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        data = get_wallet_cashout_schedule()
        if data:
            return Response(
                data={"detail": data},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Failed to get Cashout Schedule"},
            status=status.HTTP_403_FORBIDDEN,
        )


class GetMaxWalletAmountView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        wallet = request.data.get("wallet")
        amount = request.data.get("amount")
        if wallet is not None and amount is not None:
            activities = (
                Activity.objects.filter(account__user=self.request.user, wallet=wallet)
                .values("activity_type")
                .annotate(
                    running_total=Case(
                        When(
                            ~Q(activity_type=ActivityType.CASHOUT),
                            then=Sum(F("activity_amount")),
                        ),
                    ),
                    activity_total=Case(
                        When(
                            Q(activity_type=ActivityType.CASHOUT),
                            then=0 - (Sum(F("activity_amount"))),
                        ),
                        When(
                            ~Q(activity_type=ActivityType.CASHOUT),
                            then=Sum(F("activity_amount")),
                        ),
                    ),
                    cashout_total=Case(
                        When(
                            Q(activity_type=ActivityType.CASHOUT),
                            then=0 - (Sum(F("activity_amount"))),
                        ),
                    ),
                )
                .order_by("-activity_total")
            )

            wallet_total = activities.aggregate(
                total=Coalesce(Sum("activity_total"), 0, output_field=DecimalField())
            ).get("total")

            if wallet_total - int(amount) >= 0:
                can_cashout, minimum_cashout_amount = compute_minimum_cashout_amount(amount, wallet)
                if can_cashout:
                    return Response(
                        data={"detail": "Cashout Available"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    data={"detail": "Minimum amount of ₱" + str(minimum_cashout_amount)},
                    status=status.HTTP_403_FORBIDDEN,
                )
            else:
                return Response(
                    data={"detail": "Cashout exceeds Balance"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                data={"detail": "No Current Balance for Cashout"},
                status=status.HTTP_403_FORBIDDEN,
            )


class GetWalletTotalCashoutView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        data, message = compute_cashout_total(request)

        if data:
            return Response(
                data={"detail": data},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": message},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GetWalletTotalFeeView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        data = get_cashout_processing_fee_percentage()
        if data:
            return Response(
                data=data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to retrieve Company Processing Fee"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RequestCashoutView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        processed_request = process_create_cashout_request(request)
        serializer = CreateUpdateActivitySerializer(data=processed_request)

        if serializer.is_valid():
            created_cashout = serializer.save()
            if created_cashout:
                return Response(data={"detail": "Cashout Request created."}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    data={"detail": "Unable to create Cashout Request."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                data={"detail": "Unable to create Cashout Request."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateCashoutStatusView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        cashout, processed_request = process_update_cashout_status(request)
        serializer = CreateUpdateActivitySerializer(cashout, data=processed_request)
        if serializer.is_valid():
            updated_cashout = serializer.save()
            if updated_cashout.status != ActivityStatus.RELEASED:
                return Response(
                    data={"detail": "Cashout updated."},
                    status=status.HTTP_201_CREATED,
                )

            payout = create_payout_activity(request, updated_cashout)
            if not payout:
                return Response(
                    data={"detail": "Unable to create Payout Activity."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            company_earning = create_company_earning_activity(request, updated_cashout)
            if not company_earning:
                return Response(
                    data={"detail": "Unable to create Company Tax Earning Activity."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                data={"detail": "Cashout updated."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                data={"detail": "Unable to update Cashout."},
                status=status.HTTP_400_BAD_REQUEST,
            )

import json
import decimal
from django.core.signing import Signer, BadSignature
from django.shortcuts import get_object_or_404
from accounts.models import Account, Registration, Code
from core.enums import Settings
from core.services import get_setting
from emails.services import construct_and_send_email_payload, render_template
from orders.models import Customer, Order, OrderAttachments
from orders.enums import OrderStatus, OrderType
from orders.serializers import OrderInfoSerializer
from products.models import ProductVariant
from settings.models import Branch


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def transform_order_form_data_to_json(request):
    data = {}
    for key, value in request.items():
        if key == "attachments":
            continue
        if type(value) != str:
            data[key] = value
            continue
        if "{" in value or "[" in value:
            try:
                data[key] = json.loads(value)
            except ValueError:
                data[key] = value
        else:
            try:
                data[key] = json.loads(value)
            except ValueError:
                data[key] = value

    return data


def get_account(account):
    if account:
        account = get_object_or_none(Account, account_id=account)
    return account


def get_or_create_customer(customer):
    obj, created = Customer.objects.get_or_create(
        name=customer.get("name"),
        email_address=customer.get("email_address"),
        contact_number=customer.get("contact_number"),
    )

    return obj


def process_order_request(request):
    total_discount = 0
    total_fees = 0
    order_amount = 0
    has_valid_code = False

    branch = get_object_or_404(Branch, branch_id=request.get("branch"))

    data = {
        "order_type": request.get("order_type"),
        "payment_method": request.get("payment_method"),
        "order_notes": request.get("order_notes"),
        "order_date": request.get("order_date"),
        "histories": request.get("histories"),
        "branch": branch.pk,
    }

    if request.get("order_type") == OrderType.DELIVERY and request.get("address"):
        data["address"] = request.get("address")
    else:
        data["address"] = {}

    promo_code = get_object_or_none(Code, code=request.get("code"))
    if promo_code:
        data["promo_code"] = promo_code.pk
        has_valid_code = True

    details, order_amount, total_discount = process_order_details(
        request.get("details"), order_amount, has_valid_code, total_discount
    )
    data["details"] = details
    data["order_amount"] = order_amount
    data["total_discount"] = total_discount

    fees, total_fees = process_fees_details(
        request.get("fees"), total_fees, has_valid_code, total_discount, request.get("order_type")
    )
    data["fees"] = fees
    data["total_fees"] = total_fees

    data["total_amount"] = (decimal.Decimal(order_amount) + decimal.Decimal(total_fees)) - decimal.Decimal(
        total_discount
    )

    return data


def process_order_details(details, order_amount, has_valid_code, total_discount):
    new_details = []
    for detail in details:
        new_detail = {}
        variant = get_object_or_none(ProductVariant, variant_id=detail.get("variant", None))
        if variant:
            new_detail["product_variant"] = variant.pk
            new_detail["quantity"] = detail.get("quantity", 0)
            new_detail["amount"] = variant.price.base_price
            new_detail["discount"] = 0
            new_detail["total_amount"] = variant.price.base_price * detail.get("quantity", 0)

            order_amount += new_detail.get("total_amount")

            if has_valid_code:
                new_detail["discount"] = variant.price.discounted_price
                total_discount += (variant.price.base_price * new_detail.get("quantity", 0)) - (
                    variant.price.discounted_price * new_detail.get("quantity", 0)
                )

        new_details.append(new_detail)

    return new_details, order_amount, total_discount


def process_fees_details(fees, total_fees, has_valid_code, total_discount, order_type):
    new_fees = []
    delivery_fee = 150

    if order_type == OrderType.DELIVERY:
        new_fee = {"fee_type": "Delivery Fee", "amount": delivery_fee}
        new_fees.append(new_fee)

    if has_valid_code:
        new_fee = {"fee_type": "Discount", "amount": -abs(total_discount)}
        new_fees.append(new_fee)

    for fee in new_fees:
        total_fees += decimal.Decimal(fee.get("amount"))

    return new_fees, total_fees


def create_order_initial_history():
    history = [{"order_status": OrderStatus.PENDING, "comment": "Order Submitted"}]

    return history


def process_order_history_request(request):
    order = get_object_or_404(Order, order_id=request.data["order_id"])

    if order:
        data = {
            "order": order.pk,
            "order_status": request.data["order_status"],
            "comment": request.data["comment"],
            "email_sent": request.data["email_sent"],
            "created_by": request.user.pk,
        }

        return data


def process_attachments(order, request):
    has_failed_upload = False
    attachments_dict = dict((request).lists())["attachments"]

    for attachment in attachments_dict:
        data = {"order": order, "attachment": attachment}
        success = OrderAttachments.objects.create(**data)
        if success is None:
            has_failed_upload = True

    return has_failed_upload


def notify_customer_on_order_update_by_email(order):
    serialized_order = OrderInfoSerializer(order)

    if serialized_order:
        shop_domain = str(get_setting(Settings.SHOP_DOMAIN))
        shop_order_link = str(get_setting(Settings.SHOP_ORDER_LINK))

        email_template = "emails/order.html"
        email_subject = "Order is " + serialized_order.data.get("current_order_status").replace("_", " ").title()

        if order.account:
            email_body = render_template(
                email_template,
                {
                    "order": serialized_order.data,
                    "link": "".join((shop_domain, shop_order_link, serialized_order.data.get("order_id"))),
                    "sub_title": "Thank you for purchasing!",
                    "title": email_subject + "!",
                },
            )
            return construct_and_send_email_payload(email_subject, email_body, order.account.user.email_address)

        email_body = render_template(
            email_template,
            {
                "order": serialized_order.data,
                "link": "".join((shop_domain, shop_order_link, serialized_order.data.get("order_id"))),
                "sub_title": "Thank you for purchasing!",
                "title": email_subject + "!",
            },
        )

        return construct_and_send_email_payload(email_subject, email_body, order.customer.email_address)

    return None


def check_for_exclusive_product_variant(order_history):
    order = get_object_or_404(Order, id=order_history.order.pk)
    registration_tag = str(get_setting(Settings.REGISTRATION_TAG))
    for details in order.details.all():
        for tag in details.product_variant.variant_tags:
            if str(tag) == registration_tag:
                return notify_customer_on_registration_by_email(order)


def notify_customer_on_registration_by_email(order):
    registration_obj = create_registration_object(order)
    if not registration_obj:
        return "Unable to send Registration Email"

    serialized_order = OrderInfoSerializer(order)

    if serialized_order:
        email_template = "emails/registration.html"
        email_subject = "Congratulations"

        member_domain = str(get_setting(Settings.MEMBER_DOMAIN))
        registration_link = str(get_setting(Settings.REGISTRATION_LINK))

        email_body = render_template(
            email_template,
            {
                "order": serialized_order.data,
                "link": "".join((member_domain, registration_link, str(registration_obj))),
                "sub_title": "Thank you for purchasing!",
                "title": email_subject + "!",
            },
        )

        return construct_and_send_email_payload(email_subject, email_body, order.customer.email_address)


def create_registration_object(order):
    registration, created = Registration.objects.get_or_create(order=order)

    signer = Signer()
    data = {
        "registration_id": registration.id,
        "customer": registration.order.customer.id,
        "order_number": str(registration.order.id).zfill(5),
    }
    signed_obj = signer.sign_object(data)

    return signed_obj

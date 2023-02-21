import json
import decimal
from django.core.signing import Signer, BadSignature
from django.shortcuts import get_object_or_404
from accounts.models import Account, Registration, Code
from core.enums import Settings
from core.services import get_setting
from emails.services import construct_and_send_email_payload, get_email_template, render_template
from orders.models import Customer, Address, Order, OrderAttachments
from orders.enums import OrderStatus
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


def get_account(request):
    account = get_object_or_none(Account, account_id=request["account"])

    return account


def get_or_create_customer(request):
    obj, created = Customer.objects.get_or_create(
        name=request["customer"]["name"],
        email_address=request["customer"]["email_address"],
        contact_number=request["customer"]["contact_number"],
    )

    if created:
        create_customer_address(obj, request["customer"]["address"])

    return obj


def create_customer_address(customer, addresses):
    for address in addresses:
        Address.objects.create(**address, customer=customer)


def process_order_request(request):
    total_amount = 0
    total_discount = 0
    total_fees = 0
    order_amount = 0
    has_valid_code = False

    branch = get_object_or_404(Branch, branch_id=request["branch"])

    data = {
        "order_type": request["order_type"],
        "payment_method": request["payment_method"],
        "order_notes": request["order_notes"],
        "order_date": request["order_date"],
        "fees": request["fees"],
        "histories": request["histories"],
        "branch": branch.pk,
    }

    if request["code"]:
        promo_code = get_object_or_none(Code, code=request["code"])
        if promo_code:
            data["promo_code"] = promo_code.pk
            has_valid_code = True

    details, order_amount, total_discount = process_order_details(
        request["details"], order_amount, has_valid_code, total_discount
    )
    data["details"] = details
    data["order_amount"] = order_amount
    data["total_discount"] = total_discount

    total_fees = process_fees_details(request["fees"], total_fees, has_valid_code, total_discount)
    data["total_fees"] = total_fees

    data["total_amount"] = (decimal.Decimal(order_amount) + decimal.Decimal(total_fees)) - decimal.Decimal(
        total_discount
    )

    return data


def process_order_details(details, order_amount, has_valid_code, total_discount):
    for detail in details:
        variant = get_object_or_none(ProductVariant, variant_id=detail["variant"])
        if variant:
            detail["product_variant"] = variant.pk
            detail["amount"] = variant.price.price
            detail["discount"] = 0
            detail["total_amount"] = variant.price.price * detail["quantity"]
            order_amount += detail["total_amount"]
            if has_valid_code:
                detail["discount"] = variant.price.discount
                detail["total_amount"] = variant.price.discount * detail["quantity"]
                total_discount += (variant.price.price * detail["quantity"]) - (
                    variant.price.discount * detail["quantity"]
                )

    return details, order_amount, total_discount


def process_fees_details(fees, total_fees, has_valid_code, total_discount):
    for detail in fees:
        total_fees += decimal.Decimal(detail["amount"])

    if has_valid_code:
        fees.append({"fee_type": "Discount", "amount": -abs(total_discount)})

    return total_fees


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


def notify_customer_on_order_update_by_email(order_history):
    order = get_object_or_404(Order, id=order_history.order.pk)

    if order:
        shop_order_link = str(get_setting(Settings.SHOP_ORDER_LINK))
        template = "%s%s" % ("ORDER_", order_history.order_status)
        email_template = get_email_template(template)
        email_subject = render_template(email_template.subject, {})
        if order.account:
            email_body = render_template(
                email_template.body,
                {
                    "customer": order.account.get_account_name,
                    "link": shop_order_link + "?id=" + str(order.order_id),
                },
            )
            return construct_and_send_email_payload(email_subject, email_body, order.account.user.email_address)

        email_body = render_template(
            email_template.body,
            {"customer": order.customer.name, "link": shop_order_link + "?id=" + str(order.order_id)},
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

    registration_link = str(get_setting(Settings.REGISTRATION_LINK))
    email_template = get_email_template("REGISTRATION")
    email_subject = render_template(
        email_template.subject,
        {"customer": order.customer.name},
    )
    email_body = render_template(
        email_template.body,
        {"customer": order.customer.name, "link": registration_link + "?data=" + str(registration_obj)},
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

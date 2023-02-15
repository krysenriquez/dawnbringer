import json
from django.shortcuts import get_object_or_404
from orders.models import Customer, Address, Order, OrderAttachments
from orders.enums import OrderStatus
from emails.services import construct_and_send_email_payload, get_email_template, render_template


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


def get_or_create_customer(request):
    print(request["customer"])
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


def process_order_request(request, customer):
    attachments = []

    data = {
        "customer": customer.pk,
        "account": request.data["account"],
        "total_amount": request.data["total_amount"],
        "total_discount": request.data["total_discount"],
        "total_fees": request.data["total_fees"],
        "order_amount": request.data["order_amount"],
        "order_type": request.data["order_type"],
        "payment_method": request.data["payment_method"],
        "order_notes": request.data["order_notes"],
        "order_date": request.data["order_date"],
        "details": request.data["details"],
        "fees": request.data["fees"],
    }

    if request.data["attachments"]:
        attachments = request.data["attachments"]

    data["histories"] = create_order_initial_history()

    return data, attachments


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
        email_template = get_email_template(order_history.order_status)
        email_subject = render_template(email_template.subject, {})
        if order.account:
            email_body = render_template(
                email_template.body,
                {
                    "customer": order.account.get_account_name,
                    "link": "http://localhost:8000/order?id=" + str(order.order_id),
                },
            )
            return construct_and_send_email_payload(email_subject, email_body, order.account.user.email_address)

        email_body = render_template(
            email_template.body,
            {"customer": order.customer.name, "link": "http://localhost:8000/order?id=" + str(order.order_id)},
        )
        return construct_and_send_email_payload(email_subject, email_body, order.customer.email_address)

    return None

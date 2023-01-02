from django.shortcuts import get_object_or_404
from orders.models import Customer, Address, Order, OrderAttachments
from orders.enums import OrderStatus


def get_or_create_customer(request):
    print(request.data)
    obj, created = Customer.objects.get_or_create(
        name=request.data["customer"]["name"],
        email_address=request.data["customer"]["email_address"],
        contact_number=request.data["customer"]["contact_number"],
    )

    if created:
        create_customer_address(obj, request.data["customer"]["address"])

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
    order = get_object_or_404(Order, id=request.data["order_number"].lstrip("0"))

    if order:
        data = {
            "order": order.pk,
            "order_status": request.data["order_status"],
            "comment": request.data["comment"],
            "created_by": request.user.pk,
        }

        return data


def process_attachments(order, attachments):
    has_failed_upload = False
    attachments_dict = dict((attachments).lists())

    for attachment in attachments_dict:
        data = {"order": order, "attachment": attachment}
        success = OrderAttachments.objects.create(**data)
        if success is None:
            has_failed_upload = True

    return has_failed_upload

from django.shortcuts import get_object_or_404
from products.models import Customer, Address, Order
from products.enums import OrderStatus


def get_or_create_customer(request):
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
        "details": request.data["details"],
        "fees": request.data["fees"],
        "attachments": request.data["attachments"],
    }

    data["histories"] = create_order_initial_history()

    return data


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

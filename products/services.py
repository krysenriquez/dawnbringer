from django.shortcuts import get_object_or_404
from products.models import Customer, Address


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

    data = {
        "customer": customer.pk,
        "account": request.data["account"],
        "total_amount": request.data["total_amount"],
        "total_discount": request.data["total_discount"],
        "total_fees": request.data["total_fees"],
        "order_amount": request.data["order_amount"],
        "details": request.data["details"],
        "fees": request.data["fees"],
    }

    return data

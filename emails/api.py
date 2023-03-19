from django.template.loader import render_to_string
from django.template import Template, Context
from rest_framework import status, views
from rest_framework.response import Response
from emails.serializers import EmailInquirySerializer


from django.shortcuts import get_object_or_404
from orders.models import Order
from orders.services import notify_customer_on_order_update_by_email, notify_customer_on_registration_by_email
from products.models import Supply
from products.services import notify_branch_to_on_supply_update_by_email


class Test(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(Order, id=request.data.get("order_id"))
        email_msg = None
        email_msg = notify_customer_on_order_update_by_email(obj)

        return Response(
            data={"detail": email_msg},
            status=status.HTTP_200_OK,
        )


class CreateInquiryView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = EmailInquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"detail": "Message Sent."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"detail": "Unable to send message."},
                status=status.HTTP_400_BAD_REQUEST,
            )

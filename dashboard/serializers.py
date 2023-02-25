from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from orders.models import Order, Customer


class CustomersListAnnotatedSerializer(ModelSerializer):
    month = serializers.CharField(required=False)
    count = serializers.IntegerField(required=False)

    class Meta:
        model = Customer
        fields = [
            "month",
            "count",
        ]

class OrdersListAnnotatedSerializer(ModelSerializer):
    month = serializers.CharField(required=False)
    count = serializers.IntegerField(required=False)

    class Meta:
        model = Order
        fields = [
            "month",
            "count",
        ]


class OrdersListSerializer(ModelSerializer):
    order_number = serializers.CharField(source="get_order_number", required=False)
    current_order_status = serializers.CharField(source="get_last_order_status", required=False)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "order_number",
            "current_order_status",
            "total_amount",
            "order_type",
        ]

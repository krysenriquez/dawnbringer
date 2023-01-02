from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from orders.models import (
    Customer,
    Address,
    Order,
    OrderDetail,
    OrderFee,
    OrderAttachments,
    OrderHistory,
)

# Orders
class AddressesSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "address1",
            "address2",
            "city",
            "zip",
            "province",
            "country",
            "address_type",
        ]


class CustomersSerializer(ModelSerializer):
    address = AddressesSerializer(many=True, required=False)

    class Meta:
        model = Customer
        fields = [
            "name",
            "email_address",
            "contact_number",
            "address",
        ]


class OrderHistorySerializer(ModelSerializer):
    order_stage = serializers.IntegerField(source="get_order_status_stage", required=False)
    created_by_name = serializers.CharField(source="created_by.get_display_name", required=False)

    class Meta:
        model = OrderHistory
        fields = ["id", "order_status", "order_stage", "comment", "created", "created_by_name", "created_by"]
        ordering = ["id"]


class CreateOrderHistorySerializer(ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = ["order", "order_status", "comment", "created_by"]


class OrderAttachmentsSerializer(ModelSerializer):
    class Meta:
        model = OrderAttachments
        fields = ["attachment"]


class OrderDetailsSerializer(ModelSerializer):
    product_variant_name = serializers.CharField(source="product_variant.get_variant_name", required=False)
    product_variant_sku = serializers.CharField(source="product_variant.get_variant_sku", required=False)
    product_variant_thumbnail = serializers.ImageField(source="product_variant.get_first_media", required=False)

    class Meta:
        model = OrderDetail
        fields = [
            "product_variant",
            "product_variant_name",
            "product_variant_sku",
            "product_variant_thumbnail",
            "quantity",
            "amount",
            "total_amount",
            "discount",
        ]


class OrderFeesSerializer(ModelSerializer):
    class Meta:
        model = OrderFee
        fields = [
            "fee_type",
            "amount",
        ]


class OrdersSerializer(ModelSerializer):
    customer = CustomersSerializer()
    details = OrderDetailsSerializer(many=True, required=False)
    fees = OrderFeesSerializer(many=True, required=False)
    histories = OrderHistorySerializer(many=True, required=False)
    latest_order_status = serializers.CharField(source="get_last_order_status", required=False)
    latest_order_stage = serializers.CharField(source="get_last_order_stage", required=False)
    attachments = OrderAttachmentsSerializer(many=True, required=False)
    order_number = serializers.CharField(source="get_order_number", required=False)

    class Meta:
        model = Order
        fields = [
            "order_number",
            "total_amount",
            "total_discount",
            "total_fees",
            "order_amount",
            "latest_order_status",
            "latest_order_stage",
            "customer",
            "payment_method",
            "order_type",
            "created",
            "details",
            "fees",
            "histories",
            "attachments",
        ]


class OrderListSerializer(ModelSerializer):
    order_number = serializers.CharField(source="get_order_number", required=False)
    latest_order_status = serializers.CharField(source="get_last_order_status", required=False)

    class Meta:
        model = Order
        fields = [
            "order_number",
            "latest_order_status",
            "total_amount",
            "order_type",
        ]


class CreateOrderSerializer(ModelSerializer):
    details = OrderDetailsSerializer(many=True, required=False)
    fees = OrderFeesSerializer(many=True, required=False)
    histories = OrderHistorySerializer(many=True, required=False)
    attachments = OrderAttachmentsSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = [
            "total_amount",
            "total_discount",
            "total_fees",
            "order_amount",
            "details",
            "fees",
            "histories",
            "customer",
            "account",
            "attachments",
        ]

    def create(self, validated_data):
        details = validated_data.pop("details")
        fees = validated_data.pop("fees")
        histories = validated_data.pop("histories")
        attachments = validated_data.pop("attachments")
        order = Order.objects.create(**validated_data)

        for detail in details:
            OrderDetail.objects.create(**detail, order=order)

        for fee in fees:
            OrderFee.objects.create(**fee, order=order)

        for history in histories:
            OrderHistory.objects.create(**history, order=order)

        for attachment in attachments:
            OrderAttachments.objects.create(**attachment, order=order)

        return order

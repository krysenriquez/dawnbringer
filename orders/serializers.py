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

# Customers
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


# Orders
class ProductVariantOrderDetailsSerializer(ModelSerializer):
    order_number = serializers.CharField(source="order.get_order_number", required=False)
    order_id = serializers.CharField(source="order.order_id", required=False)
    current_order_status = serializers.CharField(source="order.get_last_order_status", required=False)

    class Meta:
        model = OrderDetail
        fields = [
            "order_number",
            "order_id",
            "current_order_status",
            "amount",
            "discount",
            "quantity",
            "total_amount",
        ]


class OrderHistorySerializer(ModelSerializer):
    order_stage = serializers.IntegerField(source="get_order_status_stage", required=False)
    order_note = serializers.CharField(source="get_order_default_note", required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = OrderHistory
        fields = [
            "id",
            "order_status",
            "order_stage",
            "comment",
            "order_note",
            "created",
            "created_by_name",
            "created_by",
        ]
        ordering = ["id"]


class CreateOrderHistorySerializer(ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = ["order", "order_status", "comment", "email_sent", "created_by"]


class OrderAttachmentsSerializer(ModelSerializer):
    class Meta:
        model = OrderAttachments
        fields = ["attachment"]


class OrderDetailsSerializer(ModelSerializer):
    variant_name = serializers.CharField(source="product_variant.variant_name", required=False)
    variant_sku = serializers.CharField(source="product_variant.sku", required=False)
    variant_thumbnail = serializers.ImageField(source="product_variant.variant_image", required=False)

    class Meta:
        model = OrderDetail
        fields = [
            "product_variant",
            "variant_name",
            "variant_sku",
            "variant_thumbnail",
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


class OrderInfoSerializer(ModelSerializer):
    histories = OrderHistorySerializer(many=True, required=False)
    attachments = OrderAttachmentsSerializer(many=True, required=False)
    details = OrderDetailsSerializer(many=True, required=False)
    fees = OrderFeesSerializer(many=True, required=False)
    customer = CustomersSerializer()
    current_order_status = serializers.CharField(source="get_last_order_status", required=False)
    current_order_stage = serializers.CharField(source="get_last_order_stage", required=False)
    order_number = serializers.CharField(source="get_order_number", required=False)

    class Meta:
        model = Order
        fields = [
            "histories",
            "attachments",
            "details",
            "fees",
            "customer",
            "current_order_status",
            "current_order_stage",
            "order_number",
            "order_date",
            "total_amount",
            "total_discount",
            "total_fees",
            "order_amount",
            "payment_method",
            "order_type",
            "created",
        ]


class CreateOrderSerializer(ModelSerializer):
    details = OrderDetailsSerializer(many=True, required=False)
    fees = OrderFeesSerializer(many=True, required=False)
    histories = OrderHistorySerializer(many=True, required=False)

    def create(self, validated_data):
        details = validated_data.pop("details")
        fees = validated_data.pop("fees")
        histories = validated_data.pop("histories")
        order = Order.objects.create(**validated_data)

        for detail in details:
            OrderDetail.objects.create(**detail, order=order)

        for fee in fees:
            OrderFee.objects.create(**fee, order=order)

        for history in histories:
            OrderHistory.objects.create(**history, order=order)

        return order

    class Meta:
        model = Order
        fields = "__all__"

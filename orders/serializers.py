import json
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from orders.models import (
    Customer,
    Order,
    OrderDetail,
    OrderFee,
    OrderAddress,
    OrderAttachments,
    OrderHistory,
)

# Orders
class ReferralOrderDetailsSerializer(ModelSerializer):
    variant_name = serializers.CharField(source="product_variant.variant_name", required=False)
    variant_sku = serializers.CharField(source="product_variant.sku", required=False)

    def to_representation(self, instance):
        data = super(ReferralOrderDetailsSerializer, self).to_representation(instance)
        total_point_values = instance.get_total_point_values()
        data.update({"point_values": total_point_values})
        return data

    class Meta:
        model = OrderDetail
        fields = [
            "product_variant",
            "variant_name",
            "variant_sku",
            "quantity",
        ]


class ReferralOrdersListSerializer(ModelSerializer):
    order_number = serializers.CharField(source="get_order_number", required=False)
    current_order_status = serializers.CharField(source="get_last_order_status", required=False)

    def to_representation(self, instance):
        request = self.context.get("request")
        point_value_membership_name = None
        point_value_membership_level = None
        point_value = 0

        total_point_values = instance.get_order_total_point_values()
        promo_code_levels = instance.get_promo_code_account_four_levels()
        for promo_code_level in promo_code_levels:
            account = promo_code_level.get("account")

            if account.user.pk == request.user.pk:
                level = promo_code_level.get("level")
                point_value_level = total_point_values.get(level)

                point_value_membership_name = point_value_level.get("membership_level")
                point_value_membership_level = point_value_level.get("level")
                point_value = point_value_level.get("total")

        data = super(ReferralOrdersListSerializer, self).to_representation(instance)
        data.update(
            {
                "point_value_membership_name": point_value_membership_name,
                "point_value_membership_level": point_value_membership_level,
                "point_value": point_value,
            }
        )

        return data

    class Meta:
        model = Order
        fields = [
            "order_id",
            "order_number",
            "current_order_status",
            "total_amount",
            "order_type",
        ]


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


class OrderCustomersListSerializer(ModelSerializer):
    order_count = serializers.CharField(source="get_orders_count", required=False)
    customer_number = serializers.CharField(source="get_customer_number", required=False)

    class Meta:
        model = Customer
        fields = [
            "order_count",
            "customer_number",
            "name",
            "email_address",
            "contact_number",
        ]


class OrderHistorySerializer(ModelSerializer):
    order_stage = serializers.IntegerField(source="get_order_status_stage", required=False)
    order_note = serializers.CharField(source="get_order_default_note", required=False)
    created_by_name = serializers.CharField(source="created_by.display_name", required=False)

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


class OrderAddressSerializer(ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = [
            "address1",
            "address2",
            "city",
            "zip",
            "province",
            "country",
        ]


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
    address = OrderAddressSerializer(required=False)
    customer = OrderCustomersListSerializer()
    current_order_status = serializers.CharField(source="get_last_order_status", required=False)
    current_order_stage = serializers.CharField(source="get_last_order_stage", required=False)
    order_number = serializers.CharField(source="get_order_number", required=False)
    code = serializers.CharField(source="promo_code.code", required=False)
    code_account = serializers.CharField(source="promo_code.account.account_id", required=False)

    class Meta:
        model = Order
        fields = [
            "histories",
            "attachments",
            "details",
            "fees",
            "address",
            "customer",
            "order_id",
            "current_order_status",
            "current_order_stage",
            "order_number",
            "code",
            "code_account",
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
    address = OrderAddressSerializer(required=False)

    def create(self, validated_data):
        details = validated_data.pop("details")
        fees = validated_data.pop("fees")
        histories = validated_data.pop("histories")
        address = validated_data.pop("address")

        order = Order.objects.create(**validated_data)

        for detail in details:
            OrderDetail.objects.create(**detail, order=order)

        for fee in fees:
            OrderFee.objects.create(**fee, order=order)

        for history in histories:
            OrderHistory.objects.create(**history, order=order)

        OrderAddress.objects.create(**address, order=order)

        return order

    class Meta:
        model = Order
        fields = "__all__"


# Customers
class CustomersListSerializer(ModelSerializer):
    order_count = serializers.CharField(source="get_orders_count", required=False)
    customer_number = serializers.CharField(source="get_customer_number", required=False)

    class Meta:
        model = Customer
        fields = [
            "order_count",
            "customer_number",
            "name",
            "email_address",
            "contact_number",
        ]


class CustomerInfoSerializer(ModelSerializer):
    orders = OrdersListSerializer(many=True, required=False)
    order_count = serializers.CharField(source="get_orders_count", required=False)
    customer_number = serializers.CharField(source="get_customer_number", required=False)

    class Meta:
        model = Customer
        fields = [
            "orders",
            "order_count",
            "customer_number",
            "name",
            "email_address",
            "contact_number",
        ]

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from core.enums import Settings
from core.services import get_setting
from orders.models import Order, Customer
from products.models import ProductVariant


class OrdersListSerializer(ModelSerializer):
    order_number = serializers.CharField(source="get_order_number", required=False)
    current_order_status = serializers.CharField(source="get_last_order_status", required=False)
    remaining_prep_time_status = serializers.CharField(source="get_remaining_time_status", required=False)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "order_number",
            "current_order_status",
            "total_amount",
            "order_type",
            "order_date",
            "remaining_prep_time_status",
        ]


class ProductVariantsListSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", required=False)

    def to_representation(self, instance):
        request = self.context["request"]
        branch_id = request.query_params["branch_id"]
        low_stock_alert_quantity = int(get_setting(Settings.LOW_STOCK_ALERT_QUANTITY))
        stocks = instance.get_total_quantity_by_branch(branch_id=branch_id)
        stocks_status = None
        if stocks > low_stock_alert_quantity:
            stocks_status = "In Stock"
        elif stocks == 0:
            stocks_status = "No Stock"
        else:
            stocks_status = "Low Stock"

        data = super(ProductVariantsListSerializer, self).to_representation(instance)
        data.update({"stocks": stocks, "stocks_status": stocks_status})

        return data

    class Meta:
        model = ProductVariant
        fields = [
            "variant_name",
            "product_name",
            "sku",
        ]

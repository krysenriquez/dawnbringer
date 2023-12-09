from django.contrib import admin
from orders.models import (
    Customer,
    Order,
    OrderDetail,
    OrderFee,
    OrderAddress,
    OrderAttachments,
    OrderHistory,
)

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "account",
        "total_amount",
        "total_discount",
        "total_fees",
        "order_amount"
    )
    list_filter = ("account","customer")
    search_fields = ("account",)
    ordering = ("-created",)
    filter_horizontal = ()

    class Meta:
        model = Order
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = (
        "product_variant",
        "quantity",
        "amount",
        "discount",
        "total_amount",
    )
    list_filter = ("product_variant",)
    search_fields = ("product_variant",)
    ordering = ("-created",)
    filter_horizontal = ()

    class Meta:
        model = OrderDetail


admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(OrderFee)
admin.site.register(OrderAddress)
admin.site.register(OrderAttachments)
admin.site.register(OrderHistory)

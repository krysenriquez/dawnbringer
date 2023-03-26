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
    ordering = ("product_variant",)
    filter_horizontal = ()

    class Meta:
        model = OrderDetail


admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(OrderFee)
admin.site.register(OrderAddress)
admin.site.register(OrderAttachments)
admin.site.register(OrderHistory)

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


admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(OrderFee)
admin.site.register(OrderAddress)
admin.site.register(OrderAttachments)
admin.site.register(OrderHistory)

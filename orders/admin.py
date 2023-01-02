from django.contrib import admin
from orders.models import (
    Customer,
    Address,
    Order,
    OrderDetail,
    OrderFee,
    OrderAttachments,
    OrderHistory,
)


admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(OrderFee)
admin.site.register(OrderAttachments)
admin.site.register(OrderHistory)

from django.contrib import admin
from products.models import (
    Branch,
    DeliveryArea,
    ProductType,
    Product,
    ProductVariant,
    ProductMedia,
    Transfer,
    Price,
    PointValue,
    ProductVariantMeta,
    Customer,
    Address,
    Order,
    OrderDetail,
    OrderFee,
    OrderAttachments,
    OrderHistory,
)

admin.site.register(Branch)
admin.site.register(DeliveryArea)
admin.site.register(ProductType)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductMedia)
admin.site.register(Transfer)
admin.site.register(Price)
admin.site.register(PointValue)
admin.site.register(ProductVariantMeta)
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(OrderFee)
admin.site.register(OrderAttachments)
admin.site.register(OrderHistory)

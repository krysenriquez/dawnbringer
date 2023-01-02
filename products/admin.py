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

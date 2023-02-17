from django.contrib import admin
from products.models import (
    ProductType,
    ProductTypeMeta,
    Product,
    ProductMeta,
    ProductVariant,
    ProductVariantMeta,
    ProductMedia,
    Supply,
    Price,
    PointValue,
)

admin.site.register(ProductType)
admin.site.register(ProductTypeMeta)
admin.site.register(Product)
admin.site.register(ProductMeta)
admin.site.register(ProductVariant)
admin.site.register(ProductVariantMeta)
admin.site.register(ProductMedia)
admin.site.register(Supply)
admin.site.register(Price)
admin.site.register(PointValue)

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from products.models import (
    ProductType,
    ProductTypeMeta,
    Product,
    ProductMeta,
    ProductVariant,
    ProductVariantMeta,
    ProductMedia,
    Price,
    PointValue,
    Supply,
    SupplyDetail,
    SupplyHistory,
)

admin.site.register(ProductType, SimpleHistoryAdmin)
admin.site.register(ProductTypeMeta, SimpleHistoryAdmin)
admin.site.register(Product, SimpleHistoryAdmin)
admin.site.register(ProductMeta, SimpleHistoryAdmin)
admin.site.register(ProductVariant, SimpleHistoryAdmin)
admin.site.register(ProductVariantMeta, SimpleHistoryAdmin)
admin.site.register(ProductMedia, SimpleHistoryAdmin)
admin.site.register(Price, SimpleHistoryAdmin)
admin.site.register(PointValue, SimpleHistoryAdmin)
admin.site.register(Supply, SimpleHistoryAdmin)
admin.site.register(SupplyDetail, SimpleHistoryAdmin)
admin.site.register(SupplyHistory, SimpleHistoryAdmin)

from django.contrib import admin
from products.models import DeliveryArea, ProductType, Product, Supply, Offer, Price, PointValue

admin.site.register(DeliveryArea)
admin.site.register(ProductType)
admin.site.register(Product)
admin.site.register(Supply)
admin.site.register(Offer)
admin.site.register(Price)
admin.site.register(PointValue)

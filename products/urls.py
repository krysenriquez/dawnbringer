from rest_framework.routers import DefaultRouter
from products.api import (
    ProductTypesViewSet,
    ProductsListViewSet,
    ProductVariantsListViewSet,
    ProductInfoViewSet,
    ProductVariantInfoViewSet,
    OrdersListViewSet,
)

router = DefaultRouter()
router.register(r"getproducttypes", ProductTypesViewSet)
router.register(r"getproducts", ProductsListViewSet)
router.register(r"getproductvariants", ProductVariantsListViewSet)
router.register(r"getproduct", ProductInfoViewSet)
router.register(r"getproductvariant", ProductVariantInfoViewSet)

router.register(r"getorders", OrdersListViewSet)

urlpatterns = []

urlpatterns += router.urls

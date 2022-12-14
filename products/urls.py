from rest_framework.routers import DefaultRouter
from products.api import (
    ProductTypesViewSet,
    ProductsListViewSet,
    ProductVariantsListViewSet,
    ProductInfoViewSet,
    ProductVariantInfoViewSet,
    OrdersViewSet,
    OrdersListViewSet,
    CreateOrderView,
    CreateOrderHistoryView,
    Test,
    ShopProductsListViewSet,
    ShopProductsVariantsListViewSet,
)
from django.urls import path

router = DefaultRouter()
router.register(r"getproducttypes", ProductTypesViewSet)
router.register(r"getproducts", ProductsListViewSet)
router.register(r"getproductvariants", ProductVariantsListViewSet)
router.register(r"getproduct", ProductInfoViewSet)
router.register(r"getproductvariant", ProductVariantInfoViewSet)
router.register(r"getorders", OrdersListViewSet)
router.register(r"getorder", OrdersViewSet)
# Frontend
router.register(r"shop/getproducts", ShopProductsListViewSet)
router.register(r"shop/getproductvariants", ShopProductsVariantsListViewSet)

urlpatterns = [
    path("createorder/", CreateOrderView.as_view()),
    path("updateorder/", CreateOrderHistoryView.as_view()),
    path("test/", Test.as_view()),
]

urlpatterns += router.urls

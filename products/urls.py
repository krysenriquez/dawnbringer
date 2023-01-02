from rest_framework.routers import DefaultRouter
from products.api import (
    ProductTypesViewSet,
    ProductsListViewSet,
    ProductVariantsListViewSet,
    ProductInfoViewSet,
    ProductVariantInfoViewSet,
    CreateProductVariantView,
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
# Frontend
router.register(r"shop/getproducts", ShopProductsListViewSet)
router.register(r"shop/getproductvariants", ShopProductsVariantsListViewSet)

urlpatterns = [
    path("createvariant/", CreateProductVariantView.as_view()),
    path("test/", Test.as_view()),
]

urlpatterns += router.urls

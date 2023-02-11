from rest_framework.routers import DefaultRouter
from products.api import (
    ProductTypeOptionsViewSet,
    ProductTypesListViewSet,
    ProductTypeInfoViewSet,
    ProductOptionsViewSet,
    ProductsListViewSet,
    ProductVariantsListViewSet,
    ProductInfoViewSet,
    ProductVariantInfoViewSet,
    CreateProductTypeView,
    CreateProductView,
    CreateProductVariantView,
)
from django.urls import path

router = DefaultRouter()
router.register(r"getproducttypes", ProductTypesListViewSet)
router.register(r"getproducttype", ProductTypeInfoViewSet)
router.register(r"getproducttypesoptions", ProductTypeOptionsViewSet)
router.register(r"getproducts", ProductsListViewSet)
router.register(r"getproductsoptions", ProductOptionsViewSet)
router.register(r"getproductvariants", ProductVariantsListViewSet)
router.register(r"getproduct", ProductInfoViewSet)
router.register(r"getproductvariant", ProductVariantInfoViewSet)
# Frontend

urlpatterns = [
    path("createproducttype/", CreateProductTypeView.as_view()),
    path("createproduct/", CreateProductView.as_view()),
    path("createproductvariant/", CreateProductVariantView.as_view()),
]

urlpatterns += router.urls

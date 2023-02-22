from rest_framework.routers import DefaultRouter
from products.api import (
    ProductTypeOptionsViewSet,
    ProductTypesListViewSet,
    ProductTypeInfoViewSet,
    ProductOptionsViewSet,
    ProductsListViewSet,
    ProductInfoViewSet,
    ProductVariantOptionsViewSet,
    ProductVariantsListViewSet,
    ProductVariantInfoViewSet,
    SuppliesListViewSet,
    SuppliesInfoViewSet,
    VerifyProductView,
    VerifySkuView,
    CreateProductTypeView,
    UpdateProductTypeView,
    CreateProductView,
    UpdateProductView,
    CreateProductVariantView,
    UpdateProductVariantView,
    CreateSupplyView,
    UpdateSupplyView,
    CreateSupplyHistoryView,
    GetSupplyStatusView,
)
from django.urls import path

router = DefaultRouter()
router.register(r"getproducttypesoptions", ProductTypeOptionsViewSet)
router.register(r"getproducttypes", ProductTypesListViewSet)
router.register(r"getproducttype", ProductTypeInfoViewSet)
router.register(r"getproductsoptions", ProductOptionsViewSet)
router.register(r"getproducts", ProductsListViewSet)
router.register(r"getproduct", ProductInfoViewSet)
router.register(r"getproductvariantsoptions", ProductVariantOptionsViewSet)
router.register(r"getproductvariants", ProductVariantsListViewSet)
router.register(r"getproductvariant", ProductVariantInfoViewSet)
router.register(r"getsupplies", SuppliesListViewSet)
router.register(r"getsupply", SuppliesInfoViewSet)
# Frontend

urlpatterns = [
    path("verifyproductname/", VerifyProductView.as_view()),
    path("verifysku/", VerifySkuView.as_view()),
    path("createproducttype/", CreateProductTypeView.as_view()),
    path("updateproducttype/", UpdateProductTypeView.as_view()),
    path("createproduct/", CreateProductView.as_view()),
    path("updateproduct/", UpdateProductView.as_view()),
    path("createproductvariant/", CreateProductVariantView.as_view()),
    path("updateproductvariant/", UpdateProductVariantView.as_view()),
    path("createsupply/", CreateSupplyView.as_view()),
    path("updatesupply/", UpdateSupplyView.as_view()),
    path("updatesupplystatus/", CreateSupplyHistoryView.as_view()),
    path("getsupplystatus/", GetSupplyStatusView.as_view()),
]

urlpatterns += router.urls

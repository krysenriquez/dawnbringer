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
    VerifyProductTypeView,
    VerifyProductTypeSlugView,
    VerifyProductView,
    VerifyProductSlugView,
    VerifyProductVariantSkuView,
    VerifyProductVariantSlugView,
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
router.register(r"admin/getproducttypesoptions", ProductTypeOptionsViewSet)
router.register(r"admin/getproducttypes", ProductTypesListViewSet)
router.register(r"admin/getproducttype", ProductTypeInfoViewSet)
router.register(r"admin/getproductsoptions", ProductOptionsViewSet)
router.register(r"admin/getproducts", ProductsListViewSet)
router.register(r"admin/getproduct", ProductInfoViewSet)
router.register(r"admin/getproductvariantsoptions", ProductVariantOptionsViewSet)
router.register(r"admin/getproductvariants", ProductVariantsListViewSet)
router.register(r"admin/getproductvariant", ProductVariantInfoViewSet)
router.register(r"admin/getsupplies", SuppliesListViewSet)
router.register(r"admin/getsupply", SuppliesInfoViewSet)
# Frontend

urlpatterns = [
    path("admin/verifyproducttypename/", VerifyProductTypeView.as_view()),
    path("admin/verifyproducttypeslug/", VerifyProductTypeSlugView.as_view()),
    path("admin/verifyproductname/", VerifyProductView.as_view()),
    path("admin/verifyproductslug/", VerifyProductSlugView.as_view()),
    path("admin/verifyproductvariantsku/", VerifyProductVariantSkuView.as_view()),
    path("admin/verifyproductvariantslug/", VerifyProductVariantSlugView.as_view()),
    path("admin/createproducttype/", CreateProductTypeView.as_view()),
    path("admin/updateproducttype/", UpdateProductTypeView.as_view()),
    path("admin/createproduct/", CreateProductView.as_view()),
    path("admin/updateproduct/", UpdateProductView.as_view()),
    path("admin/createproductvariant/", CreateProductVariantView.as_view()),
    path("admin/updateproductvariant/", UpdateProductVariantView.as_view()),
    path("admin/createsupply/", CreateSupplyView.as_view()),
    path("admin/updatesupply/", UpdateSupplyView.as_view()),
    path("admin/updatesupplystatus/", CreateSupplyHistoryView.as_view()),
    path("admin/getsupplystatus/", GetSupplyStatusView.as_view()),
]

urlpatterns += router.urls

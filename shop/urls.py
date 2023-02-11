from rest_framework.routers import DefaultRouter
from django.urls import path
from shop.api import PageContentsViewSet, PageComponentsViewSet, SectionComponentsViewSet
from orders.api import CreateOrderView, ShopOrderInfoViewSet, ShopOrdersListViewSet
from products.api import (
    ShopProductTypesListViewSet,
    ShopProductsListViewSet,
    ShopProductsVariantsListViewSet,
    ShopProductTypeViewSet,
    ShopProductViewSet,
    ShopProductsVariantViewSet,
)
from settings.api import ShopBranchListViewSet, ShopBranchViewSet

router = DefaultRouter()
router.register(r"getpagecontents", PageContentsViewSet)
router.register(r"getpagecomponents", PageComponentsViewSet)
router.register(r"getsectioncomponents", SectionComponentsViewSet)
# Array Object
router.register(r"getproducttypes", ShopProductTypesListViewSet)
router.register(r"getproducts", ShopProductsListViewSet)
router.register(r"getproductvariants", ShopProductsVariantsListViewSet)
router.register(r"getbranches", ShopBranchListViewSet)
router.register(r"getorders", ShopOrdersListViewSet)
# Single Object - With Query Param
router.register(r"getproducttype", ShopProductTypeViewSet)
router.register(r"getproduct", ShopProductViewSet)
router.register(r"getproductvariant", ShopProductsVariantViewSet)
router.register(r"getbranch", ShopBranchViewSet)
router.register(r"getorder", ShopOrderInfoViewSet)

urlpatterns = [
    path("createorder/", CreateOrderView.as_view()),
]

urlpatterns += router.urls

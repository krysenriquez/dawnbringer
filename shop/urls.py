from rest_framework.routers import DefaultRouter
from django.urls import path
from accounts.api import VerifyCodeView
from shop.api import PageContentsViewSet, PageComponentsViewSet, SectionComponentsViewSet
from orders.api import CreateOrderView, ShopOrdersListViewSet, ShopOrderInfoViewSet, ShopOrderInfoGuestViewSet
from products.api import (
    ShopProductTypesListViewSet,
    ShopProductsListViewSet,
    ShopProductsVariantsListViewSet,
    ShopProductTypeViewSet,
    ShopProductViewSet,
    ShopProductsVariantViewSet,
)
from settings.api import ShopBranchListViewSet, ShopBranchInfoViewSet, ShopGetDeliveryAreaAmountView
from vanguard.api import AuthShopLoginView, WhoAmIShopView

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
router.register(r"getbranch", ShopBranchInfoViewSet)
router.register(r"getorder", ShopOrderInfoViewSet)
router.register(r"getorderguest", ShopOrderInfoGuestViewSet)

urlpatterns = [
    path("createorder/", CreateOrderView.as_view()),
    path("verifycode/", VerifyCodeView.as_view()),
    path("getdeliveryamount/", ShopGetDeliveryAreaAmountView.as_view()),
    path("login/", AuthShopLoginView.as_view()),
    path("whoami/", WhoAmIShopView.as_view()),
]

urlpatterns += router.urls

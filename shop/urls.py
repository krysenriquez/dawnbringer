from rest_framework.routers import DefaultRouter
from django.urls import path
from accounts.api import VerifyCodeView
from emails.api import CreateInquiryView
from orders.api import CreateOrderView, ShopOrdersListViewSet, ShopOrderInfoViewSet, ShopOrderInfoGuestViewSet
from products.api import (
    ShopProductTypesListViewSet,
    ShopProductsListViewSet,
    ShopProductsVariantsListViewSet,
    ShopProductTypeViewSet,
    ShopProductViewSet,
    ShopProductsVariantViewSet,
)
from settings.api import (
    ShopBranchListViewSet,
    ShopBranchInfoViewSet,
    ShopGetDeliveryAreaAmountView,
)
from shop.api import (
    ShopPageContentsViewSet,
    PageContentsListViewSet,
    PageContentsInfoViewSet,
    PageComponentsListViewSet,
    PageComponentsInfoViewSet,
    SectionComponentsListViewSet,
    SectionComponentsInfoViewSet,
    CreatePageContentView,
    CreatePageComponentView,
    CreateSectionComponentView,
    UpdatePageContentView,
    UpdatePageComponentView,
    UpdateSectionComponentView,
)
from vanguard.api import AuthShopLoginView, WhoAmIShopView

router = DefaultRouter()
router.register(r"admin/shop/getpagecontents", PageContentsListViewSet)
router.register(r"admin/shop/getpagecontent", PageContentsInfoViewSet)
router.register(r"admin/shop/getpagecomponents", PageComponentsListViewSet)
router.register(r"admin/shop/getpagecomponent", PageComponentsInfoViewSet)
router.register(r"admin/shop/getsectioncomponents", SectionComponentsListViewSet)
router.register(r"admin/shop/getsectioncomponent", SectionComponentsInfoViewSet)
# Front End
router.register(r"v1/shop/getpagecontents", ShopPageContentsViewSet)
# Array Object
router.register(r"v1/shop/getproducttypes", ShopProductTypesListViewSet)
router.register(r"v1/shop/getproducts", ShopProductsListViewSet)
router.register(r"v1/shop/getproductvariants", ShopProductsVariantsListViewSet)
router.register(r"v1/shop/getbranches", ShopBranchListViewSet)
router.register(r"v1/shop/getorders", ShopOrdersListViewSet)
# Single Object - With Query Param
router.register(r"v1/shop/getproducttype", ShopProductTypeViewSet)
router.register(r"v1/shop/getproduct", ShopProductViewSet)
router.register(r"v1/shop/getproductvariant", ShopProductsVariantViewSet)
router.register(r"v1/shop/getbranch", ShopBranchInfoViewSet)
router.register(r"v1/shop/getorder", ShopOrderInfoViewSet)
router.register(r"v1/shop/getorderguest", ShopOrderInfoGuestViewSet)

urlpatterns = [
    # Admin
    path("admin/shop/createpagecontent/", CreatePageContentView.as_view()),
    path("admin/shop/updatepagecontent/", UpdatePageContentView.as_view()),
    path("admin/shop/createpagecomponent/", CreatePageComponentView.as_view()),
    path("admin/shop/updatepagecomponent/", UpdatePageComponentView.as_view()),
    path("admin/shop/createsectioncomponent/", CreateSectionComponentView.as_view()),
    path("admin/shop/updatesectioncomponent/", UpdateSectionComponentView.as_view()),
    # Front End
    path("v1/shop/createorder/", CreateOrderView.as_view()),
    path("v1/shop/verifycode/", VerifyCodeView.as_view()),
    path("v1/shop/getdeliveryamount/", ShopGetDeliveryAreaAmountView.as_view()),
    path("v1/shop/createinquiry/", CreateInquiryView.as_view()),
    path("v1/shop/login/", AuthShopLoginView.as_view()),
    path("v1/shop/whoami/", WhoAmIShopView.as_view()),
]

urlpatterns += router.urls

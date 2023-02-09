from rest_framework.routers import DefaultRouter
from django.urls import path
from shop.api import PageContentsViewSet, PageComponentsViewSet, SectionComponentsViewSet
from orders.api import CreateOrderView
from products.api import ShopProductTypesListViewSet, ShopProductsListViewSet, ShopProductsVariantsListViewSet
from settings.api import BranchViewSet

router = DefaultRouter()
router.register(r"getpagecontents", PageContentsViewSet)
router.register(r"getpagecomponents", PageComponentsViewSet)
router.register(r"getsectioncomponents", SectionComponentsViewSet)
router.register(r"getproducttypes", ShopProductTypesListViewSet)
router.register(r"getproducts", ShopProductsListViewSet)
router.register(r"getproductvariants", ShopProductsVariantsListViewSet)
router.register(r"getbranches", BranchViewSet)

urlpatterns = [
    path("createorder/", CreateOrderView.as_view()),
]

urlpatterns += router.urls

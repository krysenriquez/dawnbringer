from rest_framework.routers import DefaultRouter
from orders.api import (
    OrdersListAdminViewSet,
    OrdersListMemberViewSet,
    OrderInfoAdminViewSet,
    OrderInfoMemberViewSet,
    ReferralOrdersListMemberViewSet,
    CustomersListViewSet,
    CustomersInfoViewSet,
    GetOrderStatusView,
    VerifyOrderStocksView,
    CreateOrderHistoryView,
)
from django.urls import path

router = DefaultRouter()
# Admin
router.register(r"getadminorders", OrdersListAdminViewSet)
router.register(r"getadminorder", OrderInfoAdminViewSet)
router.register(r"getcustomers", CustomersListViewSet)
router.register(r"getcustomer", CustomersInfoViewSet)
# Members
router.register(r"getorders", OrdersListMemberViewSet)
router.register(r"getorder", OrderInfoMemberViewSet)
router.register(r"getreferralorders", ReferralOrdersListMemberViewSet)
urlpatterns = [
    # Admin
    path("getorderstatus/", GetOrderStatusView.as_view()),
    path("verifyorderstocks/", VerifyOrderStocksView.as_view()),
    path("updateorder/", CreateOrderHistoryView.as_view()),
]

urlpatterns += router.urls

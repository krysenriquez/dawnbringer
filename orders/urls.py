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
router.register(r"admin/getorders", OrdersListAdminViewSet)
router.register(r"admin/getorder", OrderInfoAdminViewSet)
router.register(r"admin/getcustomers", CustomersListViewSet)
router.register(r"admin/getcustomer", CustomersInfoViewSet)
# Members
router.register(r"member/getorders", OrdersListMemberViewSet)
router.register(r"member/getorder", OrderInfoMemberViewSet)
router.register(r"member/getreferralorders", ReferralOrdersListMemberViewSet)
urlpatterns = [
    # Admin
    path("admin/getorderstatus/", GetOrderStatusView.as_view()),
    path("admin/verifyorderstocks/", VerifyOrderStocksView.as_view()),
    path("admin/updateorder/", CreateOrderHistoryView.as_view()),
]

urlpatterns += router.urls

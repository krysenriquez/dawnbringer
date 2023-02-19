from rest_framework.routers import DefaultRouter
from orders.api import (
    OrdersListAdminViewSet,
    OrdersListMemberViewSet,
    OrderInfoAdminViewSet,
    OrderInfoMemberViewSet,
    GetOrderStatusView,
    CreateOrderHistoryView,
)
from django.urls import path

router = DefaultRouter()
# Admin
router.register(r"getadminorders", OrdersListAdminViewSet)
router.register(r"getadminorder", OrderInfoAdminViewSet)
# Members
router.register(r"getorders", OrdersListMemberViewSet)
router.register(r"getorder", OrderInfoMemberViewSet)

urlpatterns = [
    # Admin
    path("getorderstatus/", GetOrderStatusView.as_view()),
    path("updateorder/", CreateOrderHistoryView.as_view()),
]

urlpatterns += router.urls

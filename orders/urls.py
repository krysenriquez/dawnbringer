from rest_framework.routers import DefaultRouter
from orders.api import (
    OrderInfoViewSet,
    OrdersListViewSet,
    GetOrderStatus,
    CreateOrderHistoryView,
)
from django.urls import path

router = DefaultRouter()
router.register(r"getorders", OrdersListViewSet)
router.register(r"getorder", OrderInfoViewSet)

urlpatterns = [
    path("getorderstatus/", GetOrderStatus.as_view()),
    path("updateorder/", CreateOrderHistoryView.as_view()),
]

urlpatterns += router.urls

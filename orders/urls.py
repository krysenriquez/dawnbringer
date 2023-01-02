from rest_framework.routers import DefaultRouter
from orders.api import (
    OrdersViewSet,
    OrdersListViewSet,
    CreateOrderView,
    CreateOrderHistoryView,
)
from django.urls import path

router = DefaultRouter()
router.register(r"getorders", OrdersListViewSet)
router.register(r"getorder", OrdersViewSet)

urlpatterns = [
    path("createorder/", CreateOrderView.as_view()),
    path("updateorder/", CreateOrderHistoryView.as_view()),
]

urlpatterns += router.urls

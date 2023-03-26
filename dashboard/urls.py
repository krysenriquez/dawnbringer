from rest_framework.routers import DefaultRouter
from django.urls import path
from dashboard.api import (
    PendingOrdersListAdminViewSet,
    GetOrdersListbyMonthAdminViewSet,
    GetOrdersStatusListbyMonthAdminViewSet,
    OrdersCountView,
    OrdersSalesView,
    CodeUsageCountView,
    CustomersCountView,
)

router = DefaultRouter()

router.register(r"getpendingorders", PendingOrdersListAdminViewSet)
router.register(r"getmonthlyorders", GetOrdersListbyMonthAdminViewSet)
router.register(r"getmonthlyordersbystatus", GetOrdersStatusListbyMonthAdminViewSet)

urlpatterns = [
    path("orderscount/", OrdersCountView.as_view()),
    path("totalsales/", OrdersSalesView.as_view()),
    path("codeusagecount/", CodeUsageCountView.as_view()),
    path("customerscount/", CustomersCountView.as_view()),
]

urlpatterns += router.urls

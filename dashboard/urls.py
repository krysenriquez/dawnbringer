from rest_framework.routers import DefaultRouter
from django.urls import path
from dashboard.api import (
    PendingOrdersListAdminViewSet,
    GetOrdersListbyMonthAdminViewSet,
    GetOrdersStatusListbyMonthAdminViewSet,
)

router = DefaultRouter()

router.register(r"getpendingorders", PendingOrdersListAdminViewSet)
router.register(r"getmonthlyorders", GetOrdersListbyMonthAdminViewSet)

urlpatterns = []

urlpatterns += router.urls

from rest_framework.routers import DefaultRouter
from django.urls import path
from dashboard.api import (
    PendingOrdersListAdminViewSet,
    ProductVariantStocksListAdminViewSet,
    CustomersCountView,
    OrdersCountSummaryView,
    OrdersSalesSummaryView,
    TotalSalesSummaryView,
    OrdersStatusView,
    CodeUsageCountView,
    CustomersCountView,
    OrdersCountView,
    MembersCountView,
    TotalSalesView,
    ProductVariantQuantitySoldView,
    ProductVariantOrdersTotalSalesView,
)

router = DefaultRouter()

router.register(r"admin/getpendingorders", PendingOrdersListAdminViewSet)
router.register(r"admin/productvariantstocks", ProductVariantStocksListAdminViewSet)

urlpatterns = [
    path("admin/orderscountsummary/", OrdersCountSummaryView.as_view()),
    path("admin/orderssalessummary/", OrdersSalesSummaryView.as_view()),
    path("admin/totalsalessummary/", TotalSalesSummaryView.as_view()),
    # path("admin/orderscountbystatus/", OrdersStatusView.as_view()),
    path("admin/codeusagecount/", CodeUsageCountView.as_view()),
    path("admin/customerscount/", CustomersCountView.as_view()),
    path("admin/memberscount/", MembersCountView.as_view()),
    path("admin/orderscount/", OrdersCountView.as_view()),
    path("admin/totalsales/", TotalSalesView.as_view()),
    path("admin/productvariantquantitysold/", ProductVariantQuantitySoldView.as_view()),
    path("admin/productvarianttotalsales/", ProductVariantOrdersTotalSalesView.as_view()),
]

urlpatterns += router.urls

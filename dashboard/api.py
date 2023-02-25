from django.db.models.functions import TruncMonth
from django.db.models import Prefetch, Q, Max, F, Prefetch, Count
from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from dashboard.serializers import OrdersListAnnotatedSerializer, OrdersListSerializer, CustomersListAnnotatedSerializer
from orders.enums import OrderStatus
from orders.models import Order, Customer
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser, IsMemberUser


class PendingOrdersListAdminViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        if branch_id:
            return (
                Order.objects.filter(branch__branch_id=branch_id)
                .annotate(latest_supply_status=Max("histories__created"))
                .filter(
                    Q(histories__created=F("latest_supply_status"))
                    & ~Q(
                        Q(histories__order_status=OrderStatus.COMPLETED)
                        | Q(histories__order_status=OrderStatus.CANCELLED)
                        | Q(histories__order_status=OrderStatus.REFUNDED)
                    )
                )
                .order_by("-id")
            )


class GetOrdersListbyMonthAdminViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersListAnnotatedSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        if branch_id:
            return (
                Order.objects.filter(branch__branch_id=branch_id)
                .annotate(month=TruncMonth("created"))
                .values("month")
                .annotate(count=Count("id"))
                .values("month", "count")
            )


class GetOrdersStatusListbyMonthAdminViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersListAnnotatedSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        if branch_id:
            return (
                Order.objects.filter(branch__branch_id=branch_id)
                .annotate(month=TruncMonth("created"))
                .values("month")
                .annotate(count=Count("id"))
                .values("month", "count")
            )


class GetCustomersListbyMonthAdminViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomersListAnnotatedSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return (
            Customer.objects.annotate(month=TruncMonth("created"))
            .values("month")
            .annotate(count=Count("id"))
            .values("month", "count")
        )

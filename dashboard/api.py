from django.db.models import Q, Max, F, Sum
from rest_framework import status, views
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from accounts.models import Account
from dashboard.serializers import OrdersListSerializer, ProductVariantsListSerializer
from dashboard.services import (
    get_obj_count,
    get_obj_count_group_by,
    get_obj_total,
    get_obj_total_group_by,
    get_obj_aggregate_count,
    get_obj_aggregate_total,
)
from orders.enums import OrderStatus
from orders.models import Order, Customer
from products.models import ProductVariant
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser


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


class ProductVariantStocksListAdminViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        return ProductVariant.objects.all().order_by("product")


class OrdersCountSummaryView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            orders = Order.objects.filter(Q(branch__branch_id=branch_id))
            serialized_data = get_obj_count(orders, period, "id", "order_date")
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Order Count Summary."},
            status=status.HTTP_404_NOT_FOUND,
        )


class OrdersSalesSummaryView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            orders = Order.objects.filter(
                Q(branch__branch_id=branch_id) & Q(histories__order_status=OrderStatus.COMPLETED)
            )
            total_amount = get_obj_total(orders, period, "total_amount", "order_date")
            total_discount = get_obj_total(orders, period, "total_discount", "order_date")
            return Response(
                data={
                    "total_amount": total_amount,
                    "total_discount": total_discount,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Order Sales Summary."},
            status=status.HTTP_404_NOT_FOUND,
        )


class TotalSalesSummaryView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            data = []
            orders = Order.objects.filter(Q(branch__branch_id=branch_id))
            total_amount = get_obj_aggregate_total(orders, period, "total_amount", "order_date", "Total Amount")
            total_discount = get_obj_aggregate_total(orders, period, "total_discount", "order_date", "Total Discount")
            total_fees = get_obj_aggregate_total(orders, period, "total_fees", "order_date", "Total Fees")
            order_amount = get_obj_aggregate_total(orders, period, "order_amount", "order_date", "Order Amount")
            data.append((total_discount, total_fees, order_amount))

            return Response(
                data={"data": (total_discount, total_fees, order_amount), "total": total_amount},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Total Sales Summary."},
            status=status.HTTP_404_NOT_FOUND,
        )


class CodeUsageCountView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            orders = Order.objects.filter(branch__branch_id=branch_id, promo_code__isnull=False)
            serialized_data = get_obj_aggregate_count(orders, period, "id", "created", "Code usage")
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Code Usage Count."},
            status=status.HTTP_404_NOT_FOUND,
        )


class CustomersCountView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        period = request.data.get("period")
        if period:
            customers = Customer.objects.all()
            serialized_data = get_obj_aggregate_count(customers, period, "id", "created", "New Customers")
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Customers Count."},
            status=status.HTTP_404_NOT_FOUND,
        )


class MembersCountView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        period = request.data.get("period")
        if period:
            accounts = Account.objects.all()
            serialized_data = get_obj_aggregate_count(accounts, period, "id", "created", "New Members")
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Members Count."},
            status=status.HTTP_404_NOT_FOUND,
        )


class OrdersCountView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            orders = Order.objects.filter(Q(branch__branch_id=branch_id))
            serialized_data = get_obj_aggregate_count(orders, period, "id", "order_date", "New Orders")
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Orders Count."},
            status=status.HTTP_404_NOT_FOUND,
        )


class TotalSalesView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            orders = Order.objects.filter(
                Q(branch__branch_id=branch_id) & Q(histories__order_status=OrderStatus.COMPLETED)
            )
            serialized_data = get_obj_aggregate_total(
                orders, period, "total_amount", "order_date", "Total Amount", "Total Sales"
            )
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Total Sales."},
            status=status.HTTP_404_NOT_FOUND,
        )


class ProductVariantQuantitySoldView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            product_variants = ProductVariant.objects.annotate(
                quantity=Sum(
                    "orders__quantity",
                    filter=Q(
                        Q(orders__order__branch__branch_id=branch_id)
                        & Q(orders__order__histories__order_status=OrderStatus.COMPLETED)
                    ),
                )
            ).all()

            serialized_data = get_obj_total_group_by(
                product_variants, period, "sku", "quantity", "orders__order__order_date"
            )
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Product Variant Order Quantity."},
            status=status.HTTP_404_NOT_FOUND,
        )


class ProductVariantOrdersTotalSalesView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            product_variants = ProductVariant.objects.annotate(
                total_amount=Sum(
                    "orders__total_amount",
                    filter=Q(
                        Q(orders__order__branch__branch_id=branch_id)
                        & Q(orders__order__histories__order_status=OrderStatus.COMPLETED)
                    ),
                )
            ).all()

            serialized_data = get_obj_total_group_by(
                product_variants, period, "sku", "total_amount", "orders__order__order_date"
            )
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Product Variant Total Sales."},
            status=status.HTTP_404_NOT_FOUND,
        )


class OrdersStatusView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        period = request.data.get("period")
        if branch_id and period:
            orders = (
                Order.objects.annotate(last_order_history_date=Max("histories__created"))
                .filter(Q(branch__branch_id=branch_id) & Q(histories__created=F("last_order_history_date")))
                .annotate(current_order_status=F("histories__order_status"))
            )
            serialized_data = get_obj_count_group_by(orders, period, "current_order_status", "id", "order_date")
            return Response(
                data=serialized_data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": "Unable to fetch Total Sales."},
            status=status.HTTP_404_NOT_FOUND,
        )

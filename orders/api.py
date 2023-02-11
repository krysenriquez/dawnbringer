from django.db.models import Prefetch
from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from orders.enums import OrderStatus, OrderType
from orders.models import (
    Order,
    OrderHistory,
)
from orders.serializers import (
    CreateOrderSerializer,
    CreateOrderHistorySerializer,
    OrderListSerializer,
    OrdersSerializer,
)
from orders.services import (
    create_order_initial_history,
    get_or_create_customer,
    process_order_request,
    process_order_history_request,
    process_attachments,
    transform_order_form_data_to_json,
)
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser, IsMemberUser


class OrdersListViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        return Order.objects.filter(branch__branch_id=branch_id).order_by("-id")


class OrderInfoViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        order_id = self.request.query_params.get("order_id", None)
        branch_id = self.request.query_params.get("branch_id", None)

        if order_id:
            return (
                Order.objects.filter(order_id=order_id, branch__branch_id=branch_id)
                .prefetch_related(Prefetch("histories", queryset=OrderHistory.objects.order_by("-id")))
                .all()
            )


class CreateOrderView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        process_request = transform_order_form_data_to_json(request.data)
        customer = get_or_create_customer(process_request)
        if customer:
            process_request["customer"] = customer.pk
            process_request["histories"] = create_order_initial_history()
            serializer = CreateOrderSerializer(data=process_request)
            if serializer.is_valid():
                order = serializer.save()
                has_failed_upload = process_attachments(order, request.data)
                if has_failed_upload:
                    return Response(
                        data={"message": "Order created. Failed to upload attachments"},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(data={"message": "Order created."}, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(
                    data={"message": "Unable to create Order."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class CreateOrderHistoryView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        process_order_history = process_order_history_request(request)
        if process_order_history:
            serializer = CreateOrderHistorySerializer(data=process_order_history)
            if serializer.is_valid():
                serializer.save()
                return Response(data={"message": "Order updated."}, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(
                    data={"message": "Unable to update Order."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class GetOrderStatus(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        order_status = request.data.get("order_status")
        order_type = request.data.get("order_type")

        StatusFilter = []
        match order_type:
            case OrderType.PICKUP:
                StatusFilter.append(OrderStatus.AWAITING_DELIVERY)
                StatusFilter.append(OrderStatus.ON_DELIVERY)
            case OrderType.DELIVERY:
                StatusFilter.append(OrderStatus.AWAITING_PICKUP)
                StatusFilter.append(OrderStatus.ON_PICKUP)

        status_arr = []
        for os in OrderStatus:
            if os not in StatusFilter and os != order_status:
                status_arr.append(os)

        if status_arr:
            return Response(
                data={"statuses": status_arr},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                data={"message": "No Order Status available."},
                status=status.HTTP_404_NOT_FOUND,
            )


# Front End
class ShopOrdersListViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        account = self.request.query_params.get("account", None)
        if account:
            return Order.objects.filter(account=account).order_by("-id").all()


class ShopOrderInfoViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        account = self.request.query_params.get("account", None)
        if account:
            order_id = self.request.query_params.get("order_id", None)
            if order_id:
                queryset = (
                    Order.objects.filter(account=account, order_id=order_id)
                    .prefetch_related(Prefetch("histories", queryset=OrderHistory.objects.order_by("-id")))
                    .all()
                )

                return queryset

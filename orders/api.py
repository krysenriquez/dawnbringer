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
    OrdersListSerializer,
    OrderInfoSerializer,
)
from orders.services import (
    check_for_exclusive_product_variant,
    create_order_initial_history,
    get_or_create_customer,
    notify_customer_on_order_update_by_email,
    process_order_request,
    process_order_history_request,
    process_attachments,
    transform_order_form_data_to_json,
)
from users.models import User
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser, IsMemberUser


class OrdersListAdminViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        return Order.objects.filter(branch__branch_id=branch_id).order_by("-id")


class OrdersListMemberViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersListSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.pk, is_active=True)
        if user is not None:
            return Order.objects.filter(account__user=user).order_by("-id")


class OrderInfoAdminViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderInfoSerializer
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


class OrderInfoMemberViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderInfoSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.pk, is_active=True)
        order_id = self.request.query_params.get("order_id", None)

        if order_id:
            return (
                Order.objects.filter(order_id=order_id, account__user=user)
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
                        data={"detail": "Order created. Failed to upload attachments"},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(data={"detail": "Order created."}, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(
                    data={"detail": "Unable to create Order."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class CreateOrderHistoryView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        process_order_history = process_order_history_request(request)
        if process_order_history:
            serializer = CreateOrderHistorySerializer(data=process_order_history)
            if serializer.is_valid():
                order_history = serializer.save()
                email_msg = None
                if order_history.email_sent:
                    email_msg = notify_customer_on_order_update_by_email(order_history)

                if order_history.order_status == OrderStatus.COMPLETED:
                    email_msg = check_for_exclusive_product_variant(order_history)

                if not email_msg:
                    return Response(data={"detail": "Order updated."}, status=status.HTTP_201_CREATED)
                return Response(data={"detail": "Order updated. " + email_msg}, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(
                    data={"detail": "Unable to update Order."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class GetOrderStatusView(views.APIView):
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
                data={"detail": "No Order Status available."},
                status=status.HTTP_404_NOT_FOUND,
            )


# Front End
class ShopOrdersListViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersListSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        account = self.request.query_params.get("account", None)
        if account:
            return Order.objects.filter(account=account).order_by("-id").all()


class ShopOrderInfoViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderInfoSerializer
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


class ShopOrderInfoGuestViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderInfoSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        order_id = self.request.query_params.get("order_id", None)
        if order_id:
            queryset = (
                Order.objects.filter(order_id=order_id)
                .prefetch_related(Prefetch("histories", queryset=OrderHistory.objects.order_by("-id")))
                .all()
            )

            return queryset

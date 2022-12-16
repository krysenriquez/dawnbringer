from django.db.models import Prefetch
from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from products.models import (
    ProductType,
    Product,
    ProductVariant,
    Order,
    OrderHistory,
    ProductMedia,
    ProductVariantMeta,
)
from products.serializers import (
    CreateOrderSerializer,
    CreateOrderHistorySerializer,
    CreateProductVariantsSerializer,
    OrderListSerializer,
    ProductTypesSerializer,
    ProductsListSerializer,
    ProductVariantsListSerializer,
    ProductInfoSerializer,
    ProductVariantInfoSerializer,
    OrdersSerializer,
    ShopProductsVariantsListSerializer,
    ShopProductsListSerializer,
)
from products.services import (
    get_or_create_customer,
    process_media,
    process_order_request,
    process_order_history_request,
    process_attachments,
    process_variant_request,
)
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser


class ProductTypesViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypesSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = ProductType.objects.all().order_by("type")

        return queryset


class ProductVariantsListViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        variant_id = self.request.query_params.get("variant_id", None)
        sku = self.request.query_params.get("sku", None)

        queryset = ProductVariant.objects.all().order_by("product")
        if variant_id:
            queryset = queryset.filter(variant_id=variant_id)

        if sku:
            queryset = queryset.filter(sku=sku)

        return queryset


class ProductsListViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id", None)

        queryset = Product.objects.all().order_by("product_type")
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        return queryset


class ProductInfoViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id", None)
        if product_id:
            queryset = Product.objects.exclude(is_deleted=True).filter(product_id=product_id)

            return queryset


class ProductVariantInfoViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        sku = self.request.query_params.get("sku", None)
        if sku:
            queryset = ProductVariant.objects.exclude(is_deleted=True).filter(sku=sku)

            return queryset


# Orders
class OrdersViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        order_id = self.request.query_params.get("order_id", None)

        queryset = Order.objects.prefetch_related(
            Prefetch("histories", queryset=OrderHistory.objects.order_by("-id"))
        ).all()
        if order_id:
            queryset = queryset.filter(id=order_id.lstrip("0"))

        return queryset


class OrdersListViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Order.objects.all().order_by("-id")


# FrontEnd
class ShopProductsVariantsListViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ShopProductsVariantsListSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        return ProductVariant.objects.all().order_by("-id")


class ShopProductsListViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ShopProductsListSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        slug = self.request.query_params.get("slug", None)
        meta = ProductVariantMeta.objects.get(page_slug=slug)

        return Product.objects.filter(enabled_variant=meta.variant)


# POST Views
class CreateProductVariantView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        process_request, media = process_variant_request(request)

        serializer = CreateProductVariantsSerializer(data=process_request)
        # print(serializer)
        if serializer.is_valid():
            variant = serializer.save()
            has_failed_upload = process_media(variant, media)
            if has_failed_upload:
                return Response(
                    data={"message": "Variant created. Failed to upload attachments"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(data={"message": "Variant created."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"message": "Unable to create Variant."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateOrderView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(request)
        if customer:
            process_request, attachments = process_order_request(request, customer)
            serializer = CreateOrderSerializer(data=process_request)
            if serializer.is_valid():
                order = serializer.save()
                has_failed_upload = process_attachments(order, attachments)
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


class Test(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        attachments = dict((request.data).lists())["attachments"]
        print(attachments)
        variant = ProductVariant.objects.get(id=2)
        for attachment in attachments:
            data = {"variant": variant, "attachment": attachment}
            success = ProductMedia.objects.create(**data)
            if success:
                print(success)
        return Response(data={"message": "Order updated."}, status=status.HTTP_201_CREATED)

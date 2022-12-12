from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from products.models import ProductType, Product, ProductVariant, Order
from products.serializers import (
    ProductTypesSerializer,
    ProductsListSerializer,
    ProductVariantsListSerializer,
    ProductInfoSerializer,
    ProductVariantInfoSerializer,
    OrdersSerializer,
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


class OrdersListViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        id = self.request.query_params.get("id", None)

        queryset = Order.objects.all()
        if id:
            queryset = queryset.filter(id=id)

        return queryset

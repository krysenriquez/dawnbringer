from django.db.models import Prefetch
from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from products.models import (
    ProductType,
    Product,
    ProductVariant,
    ProductMedia,
    ProductVariantMeta,
)
from products.serializers import (
    CreateProductVariantsSerializer,
    ProductTypesSerializer,
    ProductsListSerializer,
    ProductVariantsListSerializer,
    ProductInfoSerializer,
    ProductVariantInfoSerializer,
    ShopProductsVariantsListSerializer,
    ShopProductsListSerializer,
)
from products.services import (
    process_media,
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
        variant_id = self.request.query_params.get("variant_id", None)
        if slug:
            meta = ProductVariantMeta.objects.get(page_slug=slug)

            return Product.objects.filter(enabled_variant=meta.variant)

        if variant_id:
            variant = ProductVariantMeta.objects.get(variant_id=variant_id)
            return Product.objects.filter(enabled_variant=variant.variant)

        return Product.objects.all()


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

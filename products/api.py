from django.db.models import Prefetch
from rest_framework import status, views, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from products.enums import Status
from products.models import (
    ProductType,
    Product,
    ProductVariant,
    ProductMedia,
    ProductVariantMeta,
)
from products.serializers import (
    CreateProductSerializer,
    CreateProductTypeSerializer,
    CreateProductVariantsSerializer,
    ProductTypeInfoSerializer,
    ProductTypeListSerializer,
    ProductsListSerializer,
    ProductVariantsListSerializer,
    ProductInfoSerializer,
    ProductVariantInfoSerializer,
    ProductTypeOptionsSerializer,
    ProductOptionsSerializer,
    ShopProductsVariantsSerializer,
    ShopProductsSerializer,
    ShopProductTypesSerializer,
)
from products.services import (
    create_variant_initial_transfer,
    process_media,
    transform_form_data_to_json,
    transform_variant_form_data_to_json,
)
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser


class ProductTypeOptionsViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeOptionsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return ProductType.objects.all().order_by("product_type")


class ProductTypesListViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return ProductType.objects.all().order_by("product_type")


class ProductTypeInfoViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        product_type_id = self.request.query_params.get("product_type_id", None)
        return ProductType.objects.filter(product_type_id=product_type_id)


class ProductOptionsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductOptionsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Product.objects.all().order_by("product_type")


class ProductsListViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Product.objects.all().order_by("product_type")


class ProductInfoViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id", None)
        if product_id:
            return Product.objects.exclude(is_deleted=True).filter(product_id=product_id)


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


class ProductVariantInfoViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        sku = self.request.query_params.get("sku", None)
        if sku:
            return ProductVariant.objects.exclude(is_deleted=True).filter(sku=sku)


# POST Views
class CreateProductTypeView(views.APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        process_request = transform_form_data_to_json(request.data)
        process_request["created_by"] = request.user.pk
        serializer = CreateProductTypeSerializer(data=process_request)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": "Product Type created."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"message": "Unable to create Product Type."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateProductView(views.APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        process_request = transform_form_data_to_json(request.data)
        process_request["created_by"] = request.user.pk
        serializer = CreateProductSerializer(data=process_request)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": "Product created."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"message": "Unable to create Product."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateProductVariantView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        process_request = transform_variant_form_data_to_json(request.data)
        process_request["created_by"] = request.user.pk
        process_request["supplies"] = create_variant_initial_transfer(process_request, request)

        serializer = CreateProductVariantsSerializer(data=process_request)
        if serializer.is_valid():
            variant = serializer.save()
            has_failed_upload = process_media(variant, request.data)
            if has_failed_upload:
                return Response(
                    data={"message": "Variant created. Failed to upload attachments"}, status=status.HTTP_201_CREATED
                )
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


# Front End
class ShopProductTypesListViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ShopProductTypesSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        return (
            ProductType.objects.filter(product_type_status=Status.ACTIVE)
            .prefetch_related(
                Prefetch(
                    "products",
                    queryset=Product.objects.filter(product_status=Status.ACTIVE).order_by("-id"),
                )
            )
            .order_by("-id")
        )


class ShopProductTypeViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ShopProductTypesSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        slug = self.request.query_params.get("slug", None)
        if slug:
            return (
                ProductType.objects.filter(product_type_status=Status.ACTIVE, meta__page_slug=slug)
                .prefetch_related(
                    Prefetch(
                        "products",
                        queryset=Product.objects.filter(product_status=Status.ACTIVE).order_by("-id"),
                    )
                )
                .order_by("-id")
            )


class ShopProductsListViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ShopProductsSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        return (
            Product.objects.filter(product_status=Status.ACTIVE, product_type__product_type_status=Status.ACTIVE)
            .prefetch_related(
                Prefetch(
                    "product_variants",
                    queryset=ProductVariant.objects.filter(variant_status=Status.ACTIVE).order_by("-id"),
                )
            )
            .order_by("-id")
        )


class ShopProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ShopProductsSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        slug = self.request.query_params.get("slug", None)
        if slug:
            return (
                Product.objects.filter(
                    product_status=Status.ACTIVE, product_type__product_type_status=Status.ACTIVE, meta__page_slug=slug
                )
                .prefetch_related(
                    Prefetch(
                        "product_variants",
                        queryset=ProductVariant.objects.filter(variant_status=Status.ACTIVE).order_by("-id"),
                    )
                )
                .order_by("-id")
            )


class ShopProductsVariantsListViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ShopProductsVariantsSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        return ProductVariant.objects.filter(
            variant_status=Status.ACTIVE,
            product__product_status=Status.ACTIVE,
            product__product_type__product_type_status=Status.ACTIVE,
        ).order_by("-id")


class ShopProductsVariantViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ShopProductsVariantsSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        slug = self.request.query_params.get("slug", None)
        if slug:
            return ProductVariant.objects.filter(
                variant_status=Status.ACTIVE,
                product__product_status=Status.ACTIVE,
                product__product_type__product_type_status=Status.ACTIVE,
                meta__page_slug=slug,
            ).order_by("-id")

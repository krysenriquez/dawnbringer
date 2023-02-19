from django.db.models import Prefetch, Q, Sum, Max, F
from rest_framework import status, views, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from orders.enums import OrderStatus
from orders.models import OrderDetail
from products.enums import Status, SupplyStatus
from products.models import (
    ProductType,
    Product,
    ProductVariant,
    ProductMedia,
    ProductVariantMeta,
    Supply,
    SupplyDetail,
    SupplyHistory,
)
from products.serializers import (
    CreateProductSerializer,
    CreateProductTypeSerializer,
    CreateProductVariantsSerializer,
    CreateSupplyHistorySerializer,
    ProductTypeOptionsSerializer,
    ProductTypesListSerializer,
    ProductTypeInfoSerializer,
    ProductOptionsSerializer,
    ProductsListSerializer,
    ProductInfoSerializer,
    ProductVariantOptionsSerializer,
    ProductVariantsListSerializer,
    ProductVariantInfoSerializer,
    SuppliesListSerializer,
    SupplyCreateSerializer,
    SupplyInfoSerializer,
    ShopProductsVariantsSerializer,
    ShopProductsSerializer,
    ShopProductTypesSerializer,
)
from products.services import (
    create_supply_initial_history,
    create_supply_status_filter,
    create_variant_initial_supply,
    notify_branch_to_on_supply_update_by_email,
    process_media,
    process_supply_history_request,
    process_supply_request,
    transform_form_data_to_json,
    transform_variant_form_data_to_json,
)
from settings.models import Branch
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser

# Product Type
class ProductTypeOptionsViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeOptionsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return ProductType.objects.all().order_by("product_type")


class ProductTypesListViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypesListSerializer
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


# Product
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


# Product Variant
class ProductVariantOptionsViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantOptionsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return ProductVariant.objects.all().order_by("product")


class ProductVariantsListViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        return ProductVariant.objects.all().order_by("product")


class ProductVariantInfoViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        sku = self.request.query_params.get("sku", None)
        if sku:
            return (
                ProductVariant.objects.exclude(is_deleted=True)
                .filter(sku=sku)
                .prefetch_related(
                    Prefetch(
                        "supplies",
                        SupplyDetail.objects.annotate(latest_supply_status=Max("supply__histories__created"))
                        .filter(supply__branch_to__branch_id=branch_id)
                        .filter(
                            supply__histories__created=F("latest_supply_status"),
                            supply__histories__supply_status=SupplyStatus.DELIVERED,
                        ),
                    ),
                    Prefetch(
                        "orders",
                        OrderDetail.objects.filter(order__branch__branch_id=branch_id).filter(
                            order__histories__order_status=OrderStatus.COMPLETED
                        ),
                    ),
                )
            )


# Supplies
class SuppliesListViewSet(ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SuppliesListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        branch = Branch.objects.get(branch_id=branch_id)
        if branch.can_supply:
            return Supply.objects.filter(Q(branch_to__branch_id=branch_id) | Q(branch_from__branch_id=branch_id))

        if branch_id:
            return Supply.objects.filter(branch_to__branch_id=branch_id)


class SuppliesInfoViewSet(ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplyInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        supply_id = self.request.query_params.get("supply_id", None)
        branch_id = self.request.query_params.get("branch_id", None)
        branch = Branch.objects.get(branch_id=branch_id)
        if branch.can_supply:
            return (
                Supply.objects.filter(
                    Q(supply_id=supply_id) & (Q(branch_to__branch_id=branch_id) | Q(branch_from__branch_id=branch_id))
                )
                .prefetch_related(Prefetch("histories", queryset=SupplyHistory.objects.order_by("-id")))
                .all()
            )

        if branch_id:
            return (
                Supply.objects.filter(supply_id=supply_id, branch_to__branch_id=branch_id)
                .prefetch_related(Prefetch("histories", queryset=SupplyHistory.objects.order_by("-id")))
                .all()
            )


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
            return Response(data={"detail": "Product Type created."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"detail": "Unable to create Product Type."},
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
            return Response(data={"detail": "Product created."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"detail": "Unable to create Product."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateProductVariantView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        process_request = transform_variant_form_data_to_json(request.data)
        process_request["created_by"] = request.user.pk
        process_request["supplies"] = create_variant_initial_supply(process_request, request)

        serializer = CreateProductVariantsSerializer(data=process_request)
        if serializer.is_valid():
            variant = serializer.save()
            has_failed_upload = process_media(variant, request.data)
            if has_failed_upload:
                return Response(
                    data={"detail": "Variant created. Failed to upload attachments"}, status=status.HTTP_201_CREATED
                )
            return Response(data={"detail": "Variant created."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"detail": "Unable to create Variant."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateSupplyView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        processed_request = process_supply_request(request.data)
        processed_request["created_by"] = request.user.pk
        processed_request["histories"] = create_supply_initial_history(request.data)
        serializer = SupplyCreateSerializer(data=processed_request)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"detail": "Supply Request created."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"detail": "Unable to create Supply Request."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateSupplyView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        supply = Supply.objects.get(supply_id=request.data["supply_id"])
        serializer = SupplyCreateSerializer(supply, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"detail": "Supply Request updated."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"detail": "Unable to update Supply Request."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateSupplyHistoryView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        processed_supply_history = process_supply_history_request(request)
        if processed_supply_history:
            serializer = CreateSupplyHistorySerializer(data=processed_supply_history)
            if serializer.is_valid():
                supply_history = serializer.save()
                email_msg = None
                if supply_history.email_sent:
                    email_msg = notify_branch_to_on_supply_update_by_email(supply_history)
                if not email_msg:
                    return Response(data={"detail": "Supply updated."}, status=status.HTTP_201_CREATED)
                return Response(data={"detail": "Supply updated. " + email_msg}, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(
                    data={"detail": "Unable to update Supply."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class GetSupplyStatusView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        branch_id = request.data.get("branch_id")
        supply_id = request.data.get("supply_id")
        supply_status = request.data.get("supply_status")

        StatusFilter = create_supply_status_filter(branch_id, supply_id, supply_status)

        status_arr = []
        for ss in SupplyStatus:
            if ss in StatusFilter and ss != supply_status:
                status_arr.append(ss)

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

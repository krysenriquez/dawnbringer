from rest_framework.viewsets import ModelViewSet
from products.models import ProductType, Product
from products.serializers import ProductTypesSerializer, ProductsSerializer
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser


class ProductTypesViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypesSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = ProductType.objects.all().order_by("type")

        return queryset


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id", None)
        sku = self.request.query_params.get("sku", None)

        queryset = Product.objects.all().order_by("product_type")
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        if sku:
            queryset = queryset.filter(sku=sku)

        return queryset

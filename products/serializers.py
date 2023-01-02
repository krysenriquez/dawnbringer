from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from products.models import (
    Product,
    ProductType,
    ProductVariant,
    ProductMedia,
    ProductVariantMeta,
    Price,
    PointValue,
    Transfer,
    Transfer,
)


class ProductTypesSerializer(ModelSerializer):
    class Meta:
        model = ProductType
        fields = [
            "type",
        ]


# Products
class TransfersSerializer(ModelSerializer):
    class Meta:
        model = Transfer
        fields = "__all__"


class PointValuesSerializer(ModelSerializer):
    class Meta:
        model = PointValue
        fields = "__all__"


class ProductVariantMetaSerializer(ModelSerializer):
    class Meta:
        model = ProductVariantMeta
        fields = "__all__"


class ProductMediasSerializer(ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = "__all__"


class PricesSerializer(ModelSerializer):
    class Meta:
        model = Price
        fields = "__all__"


class ProductVariantsListSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", required=False)
    price = serializers.DecimalField(source="price.product_price", decimal_places=2, max_digits=13)
    media = ProductMediasSerializer(many=True, required=False)
    created_by_name = serializers.CharField(source="created_by.get_display_name", required=False)

    class Meta:
        model = ProductVariant
        fields = [
            "variant_name",
            "sku",
            "product_name",
            "price",
            "media",
            "variant_status",
            "created_by_name",
        ]


class ProductVariantInfoSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", required=False)
    price = serializers.DecimalField(source="price.product_price", decimal_places=2, max_digits=13)
    discount = serializers.DecimalField(source="price.discount", decimal_places=2, max_digits=13)
    created_by_name = serializers.CharField(source="created_by.get_display_name", required=False)
    media = ProductMediasSerializer(many=True, required=False)
    meta = ProductVariantMetaSerializer()

    class Meta:
        model = ProductVariant
        fields = [
            "variant_name",
            "sku",
            "variant_description",
            "product_name",
            "price",
            "discount",
            "media",
            "created_by_name",
            "created",
            "modified",
            "meta",
        ]


class CreateProductVariantsSerializer(ModelSerializer):
    price = PricesSerializer(required=False)
    meta = ProductVariantMetaSerializer(required=False)
    point_values = PointValuesSerializer(many=True, required=False)
    supplies = TransfersSerializer(many=True, required=False)

    def create(self, validated_data):
        price = validated_data.pop("price")
        meta = validated_data.pop("meta")
        point_values = validated_data.pop("point_values")
        supplies = validated_data.pop("supplies")

        variant = ProductVariant.objects.create(**validated_data)

        Price.objects.create(**price, variant=variant)

        ProductVariantMeta.objects.create(**meta, variant=variant)

        for point_value in point_values:
            PointValue.objects.create(**point_value, variant=variant)

        for supply in supplies:
            Transfer.objects.create(**supply, variant=variant)

        return variant

    def update(self, instance, validated_data):
        price = validated_data.get("price")
        point_values = validated_data.get("point_values")
        media = validated_data.get("media")

        instance.variant_name = validated_data.get("variant_name", instance.variant_name)
        instance.variant_description = validated_data.get("variant_description", instance.variant_description)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.save()

        keep_media = []
        if media:
            for variant_media in media:
                if "id" in variant_media.keys():
                    if ProductMedia.objects.filter(id=media["id"]).exists():
                        e = ProductMedia.objects.get(id=media["id"])
                        e.file_name = validated_data.get("file_name", e.file_name)
                        e.attachment = validated_data.get("attachment", e.attachment)
                        e.save()
                        keep_media.append(e.id)
                    else:
                        continue
                else:
                    e = ProductMedia.objects.create(**variant_media, variant=instance)
                    keep_media.append(e.id)

            for variant_media in instance.media.all():
                if variant_media.id not in keep_media:
                    variant_media.delete()

        if price:
            if "id" in price.keys():
                if Price.objects.filter(id=price["id"]).exists():
                    e = Price.objects.get(id=price["id"])
                    e.product_price = validated_data.get("product_price", e.product_price)
                    e.discount = validated_data.get("discount", e.discount)
                    e.save()
            else:
                e = Price.objects.create(**price, variant=instance)

        keep_point_values = []
        if point_values:
            for point_value in point_values:
                if "id" in point_value.keys():
                    if PointValue.objects.filter(id=point_values["id"]).exists():
                        e = PointValue.objects.get(id=point_values["id"])
                        e.membership_level = validated_data.get("membership_level", e.membership_level)
                        e.point_value = validated_data.get("point_value", e.point_value)
                        e.save()
                        keep_point_values.append(e.id)
                    else:
                        continue
                else:
                    e = PointValue.objects.create(**point_value, variant=instance)
                    keep_point_values.append(e.id)

            for point_value in instance.point_values.all():
                if point_value.id not in keep_point_values:
                    point_value.delete()

    class Meta:
        model = ProductVariant
        fields = "__all__"


class ProductsSerializer(ModelSerializer):
    product_type_name = serializers.CharField(source="get_product_type_name", required=False)
    product_variants_count = serializers.CharField(source="get_all_product_variants_count", required=False)
    created_by_name = serializers.CharField(source="get_created_by_display_name", required=False)

    def create(self, validated_data):
        product_variants = validated_data.pop("product_variants")
        product = Product.objects.create(**validated_data)

        for product_variant in product_variants:
            ProductVariant.objects.create(**product_variant, product=product)

        return product

    def update(self, instance, validated_data):
        product_variants = validated_data.pop("product_variants")

        instance.product_type = validated_data.get("product_type", instance.product_type)
        instance.product_name = validated_data.get("product_name", instance.product_name)
        instance.product_description = validated_data.get("product_description", instance.product_description)
        instance.product_status = validated_data.get("product_status", instance.product_status)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.save()

        keep_product_variants = []
        if product_variants:
            for product_variant in product_variants:
                if "id" in product_variant.keys():
                    if ProductVariant.objects.filter(id=product_variants["id"]).exists():
                        e = ProductVariant.objects.get(id=product_variants["id"])
                        e.variant_name = validated_data.get("variant_name", instance.variant_name)
                        e.variant_description = validated_data.get(
                            "variant_description", instance.variant_description
                        )
                        e.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
                        e.save()
                        keep_product_variants.append(e.id)
                    else:
                        continue
                else:
                    e = ProductVariant.objects.create(**product_variant, product=instance)
                    keep_product_variants.append(e.id)

            for product_variant in instance.product_variants.all():
                if product_variant.id not in keep_product_variants:
                    product_variant.delete()

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "product_description",
            "product_type_name",
            "product_variants_count",
            "created_by_name",
        ]


class ProductsListSerializer(ModelSerializer):
    product_type_name = serializers.CharField(source="product_type.get_type_name", required=False)
    product_variants_count = serializers.CharField(source="get_all_product_variants_count", required=False)
    created_by_name = serializers.CharField(source="created_by.get_display_name", required=False)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "product_status",
            "product_type_name",
            "product_variants_count",
            "created_by_name",
        ]


class ProductInfoSerializer(ModelSerializer):
    product_variants = ProductVariantsListSerializer(many=True, required=False)
    product_type_name = serializers.CharField(source="product_type.get_type_name", required=False)
    product_variants_count = serializers.CharField(source="get_all_product_variants_count", required=False)
    created_by_name = serializers.CharField(source="created_by.get_display_name", required=False)
    enabled_variant_name = serializers.CharField(source="enabled_variant.variant_name", required=False)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "product_description",
            "product_type_name",
            "product_variants_count",
            "product_variants",
            "enabled_variant_name",
            "created_by_name",
            "product_status",
            "created",
            "modified",
        ]


# Front-End
class ShopProductsVariantsListSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", required=False)
    category = serializers.CharField(source="product.product_type.type", required=False)
    price = serializers.DecimalField(source="price.product_price", decimal_places=2, max_digits=13)
    discount = serializers.DecimalField(source="price.discount", decimal_places=2, max_digits=13)
    media = ProductMediasSerializer(many=True, required=False)
    stocks = serializers.IntegerField(source="get_total_quantity")
    meta = ProductVariantMetaSerializer()

    class Meta:
        model = ProductVariant
        fields = [
            "variant_id",
            "product_name",
            "variant_name",
            "variant_description",
            "category",
            "sku",
            "price",
            "discount",
            "media",
            "stocks",
            "meta",
        ]


# Child of ShopProductList
class ShopProductsVariantInfoSerializer(ModelSerializer):
    price = serializers.DecimalField(source="price.product_price", decimal_places=2, max_digits=13)
    discount = serializers.DecimalField(source="price.discount", decimal_places=2, max_digits=13)
    media = ProductMediasSerializer(many=True, required=False)
    stocks = serializers.IntegerField(source="get_total_quantity")
    meta = ProductVariantMetaSerializer()

    class Meta:
        model = ProductVariant
        fields = [
            "variant_id",
            "variant_name",
            "variant_description",
            "sku",
            "price",
            "discount",
            "media",
            "meta",
            "stocks",
        ]


class ShopProductsListSerializer(ModelSerializer):
    category = serializers.CharField(source="product_type.type", required=False)
    enabled_variant = ShopProductsVariantInfoSerializer()

    class Meta:
        model = Product
        fields = ["product_name", "product_description", "product_status", "category", "enabled_variant"]

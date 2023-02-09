from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from products.models import (
    Product,
    ProductMeta,
    ProductType,
    ProductTypeMeta,
    ProductVariant,
    ProductMedia,
    ProductVariantMeta,
    Price,
    PointValue,
    Transfer,
    Transfer,
)


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
    price = serializers.DecimalField(source="price.price", decimal_places=2, max_digits=13)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = ProductVariant
        fields = [
            "variant_image",
            "variant_name",
            "product_name",
            "sku",
            "price",
            "variant_status",
            "created_by_name",
        ]


class ProductVariantInfoSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", required=False)
    price = serializers.DecimalField(source="price.price", decimal_places=2, max_digits=13)
    discount = serializers.DecimalField(source="price.discount", decimal_places=2, max_digits=13)
    created_by_name = serializers.CharField(source="created_by.username", required=False)
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
                    e.price = validated_data.get("price", e.price)
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


# Product
class ProductMetaSerializer(ModelSerializer):
    class Meta:
        model = ProductMeta
        fields = "__all__"
        read_only_fields = ("product",)


class ProductOptionsSerializer(ModelSerializer):
    product_type_name = serializers.CharField(source="product_type.get_product_type_name", required=False)

    class Meta:
        model = Product
        fields = ["id", "product_name", "product_type_name"]


class ProductsListSerializer(ModelSerializer):
    product_type_name = serializers.CharField(source="product_type.get_product_type_name", required=False)
    product_variants_count = serializers.CharField(source="get_all_product_variants_count", required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "product_image",
            "product_status",
            "product_type_name",
            "product_variants_count",
            "created_by_name",
        ]


class ProductInfoSerializer(ModelSerializer):
    meta = ProductMetaSerializer(required=False)
    product_variants = ProductVariantsListSerializer(many=True, required=False)
    product_type_name = serializers.CharField(source="product_type.get_product_type_name", required=False)
    product_variants_count = serializers.CharField(source="get_all_product_variants_count", required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)
    enabled_variant_name = serializers.CharField(source="enabled_variant.variant_name", required=False)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "product_description",
            "product_image",
            "product_type_name",
            "product_variants_count",
            "product_variants",
            "enabled_variant_name",
            "created_by_name",
            "product_status",
            "created",
            "modified",
        ]


class CreateProductSerializer(ModelSerializer):
    meta = ProductMetaSerializer(required=False)

    def create(self, validated_data):
        meta = validated_data.pop("meta")
        product = Product.objects.create(**validated_data)

        ProductMeta.objects.create(**meta, product=product)

        return product

    def update(self, instance, validated_data):
        meta = validated_data.get("meta")

        instance.product_type = validated_data.get("product_type", instance.product_type)
        instance.product_name = validated_data.get("product_name", instance.product_name)
        instance.product_image = validated_data.get("product_image", instance.product_image)
        instance.product_status = validated_data.get("product_status", instance.product_status)
        instance.product_description = validated_data.get("product_description", instance.product_description)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.save()

        if meta:
            if "id" in meta.keys():
                if ProductMeta.objects.filter(id=meta["id"]).exists():
                    e = ProductMeta.objects.get(id=meta["id"])
                    e.meta_tag_title = validated_data.get("meta_tag_title", meta["meta_tag_title"])
                    e.meta_tag_description = validated_data.get("meta_tag_description", meta["meta_tag_description"])
                    e.page_slug = validated_data.get("page_slug", meta["page_slug"])
                    e.save()
            else:
                e = ProductMeta.objects.create(**meta, account=instance)

        return instance

    class Meta:
        model = Product
        fields = "__all__"


# Product Type
class ProductTypeMetaSerializer(ModelSerializer):
    class Meta:
        model = ProductTypeMeta
        fields = "__all__"
        read_only_fields = ("product_type",)


class ProductTypeOptionsSerializer(ModelSerializer):
    class Meta:
        model = ProductType
        fields = [
            "id",
            "product_type",
        ]


class ProductTypeListSerializer(ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = ProductType
        fields = [
            "product_type_id",
            "product_type",
            "product_type_image",
            "product_type_status",
            "product_type_description",
            "created_by_name",
        ]


class ProductTypeInfoSerializer(ModelSerializer):
    meta = ProductTypeMetaSerializer(required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = ProductType
        fields = [
            "product_type_id",
            "product_type",
            "product_type_image",
            "product_type_status",
            "product_type_description",
            "created_by_name",
        ]


class CreateProductTypeSerializer(ModelSerializer):
    meta = ProductTypeMetaSerializer(required=False)

    def create(self, validated_data):
        meta = validated_data.pop("meta")
        product_type = ProductType.objects.create(**validated_data)

        ProductTypeMeta.objects.create(**meta, product_type=product_type)

        return product_type

    def update(self, instance, validated_data):
        meta = validated_data.get("meta")

        instance.product_type = validated_data.get("product_type", instance.product_type)
        instance.product_type_image = validated_data.get("product_type_image", instance.product_type_image)
        instance.product_type_status = validated_data.get("product_type_status", instance.product_type_status)
        instance.product_type_description = validated_data.get(
            "product_type_description", instance.product_type_description
        )
        instance.save()

        if meta:
            if "id" in meta.keys():
                if ProductTypeMeta.objects.filter(id=meta["id"]).exists():
                    e = ProductTypeMeta.objects.get(id=meta["id"])
                    e.meta_tag_title = validated_data.get("meta_tag_title", meta["meta_tag_title"])
                    e.meta_tag_description = validated_data.get("meta_tag_description", meta["meta_tag_description"])
                    e.page_slug = validated_data.get("page_slug", meta["page_slug"])
                    e.save()
            else:
                e = ProductTypeMeta.objects.create(**meta, account=instance)

        return instance

    class Meta:
        model = ProductType
        fields = "__all__"


# Front-End
class ShopProductsVariantsListSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", required=False)
    category = serializers.CharField(source="product.product_type.type", required=False)
    price = serializers.DecimalField(source="price.price", decimal_places=2, max_digits=13)
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
class ShopProductsVariantsSerializer(ModelSerializer):
    price = serializers.DecimalField(source="price.price", decimal_places=2, max_digits=13)
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
            "variant_image",
            "sku",
            "price",
            "discount",
            "media",
            "meta",
            "stocks",
        ]


class ShopProductsSerializer(ModelSerializer):
    category = serializers.CharField(source="product_type.type", required=False)
    product_variants = ShopProductsVariantsSerializer(many=True, required=False)
    meta = ProductMetaSerializer(required=False)

    class Meta:
        model = Product
        fields = [
            "product_name",
            "product_image",
            "product_description",
            "category",
            "product_variants",
            "meta",
        ]


class ShopProductTypesSerializer(ModelSerializer):
    product_variants = ShopProductsSerializer(many=True, required=False)
    meta = ProductTypeMetaSerializer(required=False)

    class Meta:
        model = ProductType
        fields = [
            "product_type",
            "product_type_image",
            "product_type_description",
            "meta",
        ]

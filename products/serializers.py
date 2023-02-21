from django.forms.models import model_to_dict
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from orders.serializers import ProductVariantOrderDetailsSerializer
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
    Supply,
    SupplyDetail,
    SupplyHistory,
)
from settings.serializers import BranchInfoSerializer


# Supplies
class SupplyHistorySerializer(ModelSerializer):
    supply_stage = serializers.IntegerField(source="get_supply_status_stage", required=False)
    supply_note = serializers.CharField(source="get_supply_default_note", required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = SupplyHistory
        fields = [
            "supply_stage",
            "supply_note",
            "created_by_name",
            "id",
            "supply_status",
            "comment",
            "created",
            "created_by",
        ]
        ordering = ["id"]


class CreateSupplyHistorySerializer(ModelSerializer):
    class Meta:
        model = SupplyHistory
        fields = ["supply", "supply_status", "comment", "email_sent", "created_by"]


class SupplyDetailsSerializer(ModelSerializer):
    variant_sku = serializers.CharField(source="variant.sku", required=False)
    variant_name = serializers.CharField(source="variant.variant_name", required=False)
    variant_thumbnail = serializers.ImageField(source="variant.variant_image", required=False)

    class Meta:
        model = SupplyDetail
        fields = [
            "variant_sku",
            "variant_name",
            "variant_thumbnail",
            "variant",
            "quantity",
        ]


class SuppliesListSerializer(ModelSerializer):
    supply_number = serializers.CharField(source="get_supply_number", required=False)
    branch_from_name = serializers.CharField(source="branch_from.branch_name", required=False)
    branch_to_name = serializers.CharField(source="branch_to.branch_name", required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)
    current_supply_status = serializers.CharField(source="get_last_supply_status", required=False)

    class Meta:
        model = Supply
        fields = [
            "supply_id",
            "supply_number",
            "branch_from_name",
            "branch_to_name",
            "current_supply_status",
            "created_by_name",
        ]


class SupplyInfoSerializer(ModelSerializer):
    details = SupplyDetailsSerializer(many=True, required=False)
    histories = SupplyHistorySerializer(many=True, required=False)
    supply_number = serializers.CharField(source="get_supply_number", required=False)
    branch_from_name = serializers.CharField(source="branch_from.branch_name", required=False)
    branch_to_name = serializers.CharField(source="branch_to.branch_name", required=False)
    current_supply_status = serializers.CharField(source="get_last_supply_status", required=False)
    current_supply_stage = serializers.CharField(source="get_last_supply_stage", required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)
    branch_from = BranchInfoSerializer()
    branch_to = BranchInfoSerializer()

    def to_representation(self, instance):
        request = self.context["request"]
        branch_id = request.query_params["branch_id"]
        can_update_supply_status = instance.get_can_update_supply_status(branch_id=branch_id)
        data = super(SupplyInfoSerializer, self).to_representation(instance)
        data.update(
            {
                "can_update_supply_status": can_update_supply_status,
            }
        )

        return data

    class Meta:
        model = Supply
        fields = [
            "details",
            "histories",
            "supply_number",
            "branch_from_name",
            "branch_to_name",
            "current_supply_status",
            "current_supply_stage",
            "reference_number",
            "carrier",
            "carrier_contact_number",
            "tracking_number",
            "comment",
            "created",
            "created_by_name",
            "branch_from",
            "branch_to",
        ]


class SupplyCreateSerializer(ModelSerializer):
    details = SupplyDetailsSerializer(many=True, required=False)
    histories = SupplyHistorySerializer(many=True, required=False)

    def create(self, validated_data):
        details = validated_data.pop("details")
        histories = validated_data.pop("histories")
        supply = Supply.objects.create(**validated_data)

        for detail in details:
            SupplyDetail.objects.create(**detail, supply=supply)

        for history in histories:
            SupplyHistory.objects.create(**history, supply=supply)

        return supply

    def update(self, instance, validated_data):
        details = validated_data.get("details")

        instance.branch_from = validated_data.get("branch_from", instance.branch_from)
        instance.branch_to = validated_data.get("branch_to", instance.branch_to)
        instance.reference_number = validated_data.get("reference_number", instance.reference_number)
        instance.carrier = validated_data.get("carrier", instance.carrier)
        instance.carrier_contact_number = validated_data.get("carrier_contact_number", instance.carrier_contact_number)
        instance.tracking_number = validated_data.get("tracking_number", instance.tracking_number)
        instance.comment = validated_data.get("comment", instance.comment)
        instance.save()

        keep_details = []
        if details:
            for detail in details:
                if "id" in detail.keys():
                    if SupplyDetail.objects.filter(id=details["id"]).exists():
                        e = SupplyDetail.objects.get(id=details["id"])
                        e.variant = validated_data.get("variant", e.variant)
                        e.quantity = validated_data.get("quantity", e.quantity)
                        e.save()
                        keep_details.append(e.id)
                    else:
                        continue
                else:
                    e = SupplyDetail.objects.create(**detail, variant=instance)
                    keep_details.append(e.id)

            for detail in instance.details.all():
                if detail.id not in keep_details:
                    detail.delete()

        return instance

    class Meta:
        model = Supply
        fields = "__all__"


# Product Variant
class ProductVariantSupplyDetailsSerializer(ModelSerializer):
    supply_number = serializers.CharField(source="supply.get_supply_number", required=False)
    supply_id = serializers.CharField(source="supply.supply_id", required=False)
    current_supply_status = serializers.CharField(source="supply.get_last_supply_status", required=False)
    branch_from_name = serializers.CharField(source="supply.branch_from.branch_name", required=False)
    branch_to_name = serializers.CharField(source="supply.branch_to.branch_name", required=False)

    class Meta:
        model = SupplyDetail
        fields = [
            "supply_id",
            "supply_number",
            "quantity",
            "current_supply_status",
            "branch_from_name",
            "branch_to_name",
        ]


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


class ProductVariantOptionsSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = ProductVariant
        fields = ["id", "variant_image", "variant_name", "product_name", "sku", "variant_status", "created_by_name"]


class ProductVariantsListSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", required=False)
    price = serializers.DecimalField(source="price.price", decimal_places=2, max_digits=13)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    def to_representation(self, instance):
        request = self.context["request"]
        branch_id = request.query_params["branch_id"]
        stocks = instance.get_total_quantity_by_branch(branch_id=branch_id)
        data = super(ProductVariantsListSerializer, self).to_representation(instance)
        data.update(
            {
                "stocks": stocks,
            }
        )

        return data

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
    orders = ProductVariantOrderDetailsSerializer(many=True, required=False)
    supplies = ProductVariantSupplyDetailsSerializer(many=True, required=False)
    meta = ProductVariantMetaSerializer()
    media = ProductMediasSerializer(many=True, required=False)
    product_name = serializers.CharField(source="product.product_name", required=False)
    price = serializers.DecimalField(source="price.price", decimal_places=2, max_digits=13)
    discount = serializers.DecimalField(source="price.discount", decimal_places=2, max_digits=13)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    def to_representation(self, instance):
        request = self.context["request"]
        branch_id = request.query_params["branch_id"]
        stocks = instance.get_total_quantity_by_branch(branch_id=branch_id)
        data = super(ProductVariantInfoSerializer, self).to_representation(instance)
        data.update({"stocks": stocks})

        return data

    class Meta:
        model = ProductVariant
        fields = [
            "meta",
            "media",
            "supplies",
            "orders",
            "variant_image",
            "variant_name",
            "sku",
            "variant_status",
            "variant_description",
            "variant_tags",
            "product_name",
            "price",
            "discount",
            "created_by_name",
            "created",
            "modified",
        ]


class CreateProductVariantsSerializer(ModelSerializer):
    price = PricesSerializer(required=False)
    meta = ProductVariantMetaSerializer(required=False)
    point_values = PointValuesSerializer(many=True, required=False)

    def create(self, validated_data):
        price = validated_data.pop("price")
        meta = validated_data.pop("meta")
        point_values = validated_data.pop("point_values")

        variant = ProductVariant.objects.create(**validated_data)

        Price.objects.create(**price, variant=variant)

        ProductVariantMeta.objects.create(**meta, variant=variant)

        for point_value in point_values:
            PointValue.objects.create(**point_value, variant=variant)

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
    product_type_name = serializers.CharField(source="product_type.product_type", required=False)

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
    product_variants = ProductVariantOptionsSerializer(many=True, required=False)
    product_type_name = serializers.CharField(source="product_type.get_product_type_name", required=False)
    product_variants_count = serializers.CharField(source="get_all_product_variants_count", required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)
    enabled_variant_name = serializers.CharField(source="enabled_variant.variant_name", required=False)

    class Meta:
        model = Product
        fields = [
            "meta",
            "product_variants",
            "product_id",
            "product_name",
            "product_description",
            "product_image",
            "product_tags",
            "product_type_name",
            "product_variants_count",
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


class ProductTypesListSerializer(ModelSerializer):
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
    products = ProductsListSerializer(many=True, required=False)
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = ProductType
        fields = [
            "meta",
            "products",
            "product_type_id",
            "product_type",
            "product_type_image",
            "product_type_status",
            "product_type_tags",
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
    product_type = serializers.CharField(source="product.product_type.product_type", required=False)
    product_name = serializers.CharField(source="product.product_name", required=False)
    category = serializers.CharField(source="product.product_type.type", required=False)
    price = serializers.DecimalField(source="price.price", decimal_places=2, max_digits=13)
    discount = serializers.DecimalField(source="price.discount", decimal_places=2, max_digits=13)
    media = ProductMediasSerializer(many=True, required=False)
    meta = ProductVariantMetaSerializer()

    def to_representation(self, instance):
        request = self.context["request"]
        branch_id = request.query_params["branch_id"]
        stocks = instance.get_total_quantity_by_branch(branch_id=branch_id)
        data = super(ShopProductsVariantsListSerializer, self).to_representation(instance)
        data.update({"stocks": stocks})

        return data

    class Meta:
        model = ProductVariant
        fields = [
            "product_type",
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
    product_type = serializers.CharField(source="product.product_type.product_type", required=False)
    price = serializers.DecimalField(source="price.price", decimal_places=2, max_digits=13)
    discount = serializers.DecimalField(source="price.discount", decimal_places=2, max_digits=13)
    media = ProductMediasSerializer(many=True, required=False)
    meta = ProductVariantMetaSerializer()

    def to_representation(self, instance):
        data = super(ShopProductsVariantsSerializer, self).to_representation(instance)
        request = self.context["request"]
        branch_id = request.query_params.get("branch_id", None)
        if branch_id:
            stocks = instance.get_total_quantity_by_branch(branch_id=branch_id)
            data.update({"stocks": stocks})
            return data

        data.update({"stocks": 0})
        return data

    class Meta:
        model = ProductVariant
        fields = [
            "product_type",
            "variant_id",
            "variant_name",
            "variant_description",
            "variant_image",
            "sku",
            "price",
            "discount",
            "media",
            "meta",
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
    meta = ProductTypeMetaSerializer(required=False)

    class Meta:
        model = ProductType
        fields = [
            "product_type",
            "product_type_image",
            "product_type_description",
            "meta",
        ]

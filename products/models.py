import uuid
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from products.enums import Status, SupplyStatus


def product_type_image_directory(instance, filename):
    return "product-types/{0}/image/{1}".format(instance.product_type_id, filename)


def product_image_directory(instance, filename):
    return "products/{0}/image/{1}".format(instance.product_id, filename)


def product_variant_image_directory(instance, filename):
    return "product-variants/{0}/image/{1}".format(instance.sku, filename)


def product_variant_media_directory(instance, filename):
    return "product-variants/{0}/medias/{1}".format(instance.variant.sku, filename)


# Products
class ProductType(models.Model):
    product_type_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product_type = models.CharField(max_length=255, null=True, blank=True)
    product_type_image = models.ImageField(blank=True, upload_to=product_type_image_directory)
    product_type_status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    product_type_description = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    product_type_tags = ArrayField(models.CharField(max_length=255, blank=True, null=True), blank=True, null=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_product_type",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def get_product_type_name(self):
        return self.product_type

    def __str__(self):
        return "%s" % (self.product_type)


class ProductTypeMeta(models.Model):
    product_type = models.OneToOneField(
        "products.ProductType", on_delete=models.CASCADE, related_name="meta", null=True, blank=True
    )
    meta_tag_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    meta_tag_description = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    page_slug = models.SlugField(
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "%s" % (self.product_type)


class Product(models.Model):
    product_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
    )
    product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    product_image = models.ImageField(blank=True, upload_to=product_image_directory)
    product_status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    product_description = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    product_tags = ArrayField(models.CharField(max_length=255, blank=True, null=True), blank=True, null=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_product",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(
        default=False,
    )
    deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-product_id"]

    def get_all_product_variants_count(self):
        return self.product_variants.all().count()

    def __str__(self):
        return "%s : %s" % (self.product_name, self.product_type)


class ProductMeta(models.Model):
    product = models.OneToOneField("products.Product", on_delete=models.CASCADE, related_name="meta")
    meta_tag_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    meta_tag_description = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    page_slug = models.SlugField(
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "%s" % (self.product)


class ProductVariant(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="product_variants")
    variant_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sku = models.CharField(max_length=30, unique=True, null=True, blank=True)
    variant_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    variant_image = models.ImageField(blank=True, upload_to=product_variant_image_directory)
    variant_description = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    variant_tags = ArrayField(models.CharField(max_length=255, blank=True, null=True), blank=True, null=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_product_variant",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(
        default=False,
    )
    variant_status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    deleted = models.DateTimeField(blank=True, null=True)

    def get_variant_name(self):
        return self.variant_name

    def get_variant_sku(self):
        return self.sku

    def get_first_media(self):
        media = self.media.first()
        if media:
            return media.attachment

    def get_total_quantity(self):
        return self.supplies.aggregate(current_stock=Coalesce(Sum("quantity"), 0)).get("current_stock")

    class Meta:
        ordering = ["-variant_id"]

    def __str__(self):
        return "%s : %s" % (self.sku, self.variant_name)


class ProductMedia(models.Model):
    variant = models.ForeignKey(
        "products.ProductVariant", on_delete=models.CASCADE, related_name="media", null=True, blank=True
    )
    attachment = models.ImageField(blank=True, upload_to=product_variant_media_directory)
    is_default = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - %s" % (
            self.variant,
            self.attachment,
        )


class Price(models.Model):
    variant = models.OneToOneField(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="price",
        null=True,
    )
    price = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)
    discount = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.variant, self.price)


class PointValue(models.Model):
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        related_name="point_values",
        null=True,
    )
    membership_level = models.ForeignKey(
        "core.MembershipLevel",
        on_delete=models.SET_NULL,
        related_name="point_value_per_product",
        null=True,
    )
    point_value = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)

    def __str__(self):
        return "%s - %s : %s" % (self.variant, self.membership_level, self.point_value)


class ProductVariantMeta(models.Model):
    variant = models.OneToOneField(
        "products.ProductVariant", on_delete=models.CASCADE, related_name="meta", null=True, blank=True
    )
    meta_tag_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    meta_tag_description = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    page_slug = models.SlugField(
        max_length=255,
        blank=True,
        null=True,
    )


class Supply(models.Model):
    supply_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    branch_from = models.ForeignKey(
        "settings.Branch", on_delete=models.CASCADE, related_name="supplies_from", null=True, blank=True
    )
    branch_to = models.ForeignKey(
        "settings.Branch", on_delete=models.CASCADE, related_name="supplies_to", null=True, blank=True
    )
    tracking_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    carrier = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    reference_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    comment = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_supply",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def get_supply_number(self):
        return str(self.id).zfill(5)

    def get_last_supply_status(self):
        try:
            return self.histories.latest("created").supply_status
        except:
            return None

    def get_last_supply_stage(self):
        try:
            match self.histories.latest("created").supply_status:
                case SupplyStatus.PENDING:
                    return 1
                case SupplyStatus.ORDER_RECEIVED | SupplyStatus.BACK_ORDERED:
                    return 2
                case SupplyStatus.PREPARING:
                    return 3
                case SupplyStatus.IN_TRANSIT:
                    return 3
                case SupplyStatus.CANCELLED | SupplyStatus.DENIED | SupplyStatus.CANCELLED:
                    return 4
                case _:
                    None
        except:
            return None

    def __str__(self):
        return "%s - %s" % (self.branch_from, self.branch_to)


class SupplyDetails(models.Model):
    supply = models.ForeignKey(
        "products.Supply", on_delete=models.CASCADE, related_name="details", null=True, blank=True
    )
    variant = models.ForeignKey(
        "products.ProductVariant", on_delete=models.CASCADE, related_name="supplies", null=True, blank=True
    )
    quantity = models.IntegerField(
        default=0,
        blank=True,
    )

    def __str__(self):
        return "%s : %s - %s" % (self.supply, self.variant, self.quantity)


class SupplyHistory(models.Model):
    supply = models.ForeignKey(
        "products.Supply", on_delete=models.CASCADE, related_name="histories", null=True, blank=True
    )
    supply_status = models.CharField(
        max_length=255,
        choices=SupplyStatus.choices,
        default=SupplyStatus.PENDING,
    )
    comment = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    notes = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="created_supply_history", null=True, blank=True
    )

    def __str__(self):
        return "%s - %s" % (self.order, self.order_status)

    def get_supply_status_stage(self):
        match self.supply_status:
            case SupplyStatus.PENDING:
                return 1
            case SupplyStatus.ORDER_RECEIVED | SupplyStatus.BACK_ORDERED:
                return 2
            case SupplyStatus.PREPARING:
                return 3
            case SupplyStatus.IN_TRANSIT:
                return 3
            case SupplyStatus.CANCELLED | SupplyStatus.DENIED | SupplyStatus.CANCELLED:
                return 4

    def get_supply_default_note(self):
        match self.supply_status:
            case SupplyStatus.PENDING:
                return "Supply Request has been created"
            case SupplyStatus.CANCELLED:
                return "Supply Request has been cancelled"
            case SupplyStatus.ORDER_RECEIVED:
                return "Supply Request has been received"
            case SupplyStatus.BACK_ORDERED:
                return "Supply Request moved to back ordered"
            case SupplyStatus.PREPARING:
                return "Supply Request is currently being prepared"
            case SupplyStatus.IN_TRANSIT:
                return "Supply Request is currently in transit"
            case SupplyStatus.DELIVERED:
                return "Supply Request has been delivered"
            case SupplyStatus.DENIED:
                return "Supply Request has been denied"

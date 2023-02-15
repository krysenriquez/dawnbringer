import uuid
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from products.enums import Status


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


class Transfer(models.Model):
    branch = models.ForeignKey(
        "settings.Branch", on_delete=models.CASCADE, related_name="transfer", null=True, blank=True
    )
    variant = models.ForeignKey(
        "products.ProductVariant", on_delete=models.CASCADE, related_name="supplies", null=True, blank=True
    )
    quantity = models.IntegerField(
        default=0,
        blank=True,
    )
    estimated_arrival = models.DateField(
        blank=True,
        null=True,
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
        related_name="created_transfer",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.variant, self.quantity)


class PointValue(models.Model):
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        related_name="point_values",
        null=True,
    )
    membership_level = models.ForeignKey(
        "settings.MembershipLevel",
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

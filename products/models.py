import uuid
from django.db import models


class DeliveryArea(models.Model):
    area = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )

    def __str__(self):
        return "%s - %s" % (self.area, self.amount)


class ProductType(models.Model):
    type = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="product_type_created_by",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % (self.type)


class Product(models.Model):
    product_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sku = models.CharField(max_length=30, unique=True, null=True, blank=True)
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="product_created_by",
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

    def __str__(self):
        return "%s : %s" % (self.sku, self.name)


class Supply(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        related_name="supplies",
        null=True,
    )
    quantity = models.IntegerField(
        default=0,
        blank=True,
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="supply_created_by",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.product, self.quantity)


class Offer(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        related_name="offers",
        null=True,
    )
    offered_from = models.DateTimeField(blank=True, null=True)
    offered_to = models.DateTimeField(blank=True, null=True)
    is_offered = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return "%s - %s to %s : %s" % (self.product, self.offered_from, self.offered_to, self.is_offered)


class Price(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        related_name="prices",
        null=True,
    )
    product_price = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )
    discount = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )

    def __str__(self):
        return "%s - %s" % (self.product, self.product_price)


class PointValue(models.Model):
    product = models.ForeignKey(
        "products.Product",
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
    point_value = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )

    def __str__(self):
        return "%s - %s : %s" % (self.product, self.membership_level, self.point_value)

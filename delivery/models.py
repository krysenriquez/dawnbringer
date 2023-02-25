from django.db import models


class DeliveryArea(models.Model):
    delivery_area_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    zip = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    province = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self):
        return "%s" % (self.delivery_area_name)


class DeliveryBracket(models.Model):
    delivery_bracket_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(
        "settings.Branch",
        on_delete=models.SET_NULL,
        related_name="delivery_bracket",
        null=True,
        blank=True,
    )
    delivery_area = models.ManyToManyField("delivery.DeliveryArea", related_name="delivery_bracket")


class DeliveryMethod(models.Model):
    delivery_bracket = models.ForeignKey(
        "delivery.DeliveryBracket",
        on_delete=models.SET_NULL,
        related_name="delivery_methods",
        null=True,
        blank=True,
    )
    delivery_method_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    amount = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)
    quantity = models.IntegerField(
        default=0,
        blank=True,
    )
    is_active = models.BooleanField(
        default=False,
    )


class DeliveryMethodType(models.Model):
    delivery_method = models.ForeignKey(
        "delivery.DeliveryArea",
        on_delete=models.SET_NULL,
        related_name="delivery_method_types",
        null=True,
        blank=True,
    )
    delivery_method_type_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    calculation = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

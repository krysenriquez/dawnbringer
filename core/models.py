from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from simple_history.models import HistoricalRecords
from core.enums import ActivityType, ActivityStatus, WalletType, Settings


class Setting(models.Model):
    property = models.CharField(max_length=255, default=None, choices=Settings.choices)
    value = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["property"]

    def __str__(self):
        return "%s - %s" % (self.property, self.value)


class MembershipLevel(models.Model):
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    level = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return "%s - %s" % (self.name, self.level)


class Activity(models.Model):
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.SET_NULL,
        related_name="activities",
        null=True,
        blank=True,
    )
    activity_type = models.CharField(max_length=32, choices=ActivityType.choices, blank=True, null=True)
    activity_amount = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )
    status = models.CharField(
        max_length=32,
        choices=ActivityStatus.choices,
        default=ActivityStatus.REQUESTED,
    )
    wallet = models.CharField(max_length=32, choices=WalletType.choices, blank=True, null=True)
    membership_level = models.ForeignKey(
        "core.MembershipLevel",
        on_delete=models.SET_NULL,
        related_name="activities",
        null=True,
        blank=True,
    )
    product_variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        related_name="activities",
        null=True,
        blank=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="activity_content_type",
        blank=True,
        null=True,
    )
    object_id = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_activity",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(
        default=False,
    )
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ["-created", "-id"]

    def __str__(self):
        return "%s : %s : %s - %s" % (self.activity_type, self.wallet, self.activity_amount, self.account)

    def get_activity_number(self):
        return str(self.id).zfill(7)

    def get_activity_summary(self):
        detail = []
        if self.content_type:
            generic_object = self.content_type.model_class().objects.get(id=self.object_id)
            match self.activity_type:
                case ActivityType.PURCHASE:
                    detail = "Referral Link Usage on Order #%s" % (str(generic_object.pk).zfill(5))
                case ActivityType.PAYOUT:
                    detail = "Payout to Cashout %s" % (str(generic_object.pk).zfill(5))
                case ActivityType.REFERRAL_LINK_USAGE:
                    detail = "Referral Link Usage on Order #%s" % (str(generic_object.pk).zfill(5))
                case ActivityType.CASHOUT:
                    detail = "Cashout"
        else:
            match self.activity_type:
                case ActivityType.POINT_CONVERSION:
                    detail = "Converted Point Values to Peso"

        return "%s" % (detail)

    def get_content_type_model(self):
        return "%s" % (self.content_type.model)

    def get_cashout_number(self):
        return str(self.id).zfill(5)


class ActivityDetails(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="details")
    action = models.CharField(
        max_length=255,
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_activity_details",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.activity, self.action)


class CashoutMethods(models.Model):
    method_name = models.CharField(
        max_length=255,
    )
    is_disabled = models.BooleanField(
        default=False,
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_cashout_methods",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_cashout_methods",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s - %s" % (self.method_name, self.is_disabled)

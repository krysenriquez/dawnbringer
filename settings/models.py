import uuid
from django.db import models
from simple_history.models import HistoricalRecords


def company_image_directory(instance, filename):
    return "company/{0}/image/{1}".format(instance.id, filename)


class Company(models.Model):
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    domain = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    email_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    contact_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    logo = models.ImageField(blank=True, upload_to=company_image_directory)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_company",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_company",
        null=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s" % (self.name)


class Branch(models.Model):
    branch_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    branch_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    address1 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    address2 = models.CharField(
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
    phone = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    email_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    is_main = models.BooleanField(
        default=False,
    )
    can_deliver = models.BooleanField(
        default=False,
    )
    can_supply = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_branch",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_branch",
        null=True,
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["-branch_name"]

    def get_branch_full_address(self):
        return "%s %s %s %s %s" % (self.address1, self.address2, self.city, self.province, self.zip)

    def __str__(self):
        return "%s" % (self.branch_name)


class BranchAssignment(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="branch_assignment",
    )
    branch = models.ManyToManyField("settings.Branch", related_name="assignment", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_branch_assignment",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_branch_assignment",
        null=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s - %s" % (self.user, self.branch)


class DeliveryArea(models.Model):
    branch = models.ForeignKey(
        "settings.Branch", on_delete=models.CASCADE, related_name="delivery_area", null=True, blank=True
    )
    area = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_delivery_area",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_delivery_area",
        null=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s - %s" % (self.area, self.amount)

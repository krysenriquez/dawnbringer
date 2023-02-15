import uuid
from django.db import models
from settings.enums import Settings


def company_image_directory(instance, filename):
    return "company/{0}/image/{1}".format(instance.id, filename)


class Setting(models.Model):
    property = models.CharField(max_length=255, default=None, choices=Settings.choices)
    value = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)

    class Meta:
        ordering = ["property"]

    def __str__(self):
        return "%s - %s" % (self.property, self.value)


class Company(models.Model):
    name = models.CharField(
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
    is_active = models.BooleanField(
        default=False,
    )
    can_deliver = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_branch",
        null=True,
    )

    class Meta:
        ordering = ["-branch_name"]

    def __str__(self):
        return "%s" % (self.branch_name)


class BranchAssignment(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="branch_assignment",
    )
    branch = models.ManyToManyField("settings.Branch", related_name="assignment")
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_branch_assignment",
        null=True,
    )


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

    def __str__(self):
        return "%s - %s" % (self.area, self.amount)


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


class EmailTemplate(models.Model):
    template_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    template = models.TextField(
        blank=True,
        null=True,
    )

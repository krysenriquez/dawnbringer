from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    PENDING = "PENDING", _("Pending")
    ACTIVE = "ACTIVE", _("Active")
    DEACTIVATED = "DEACTIVATED", _("Deactivated")
    CLOSED = "CLOSED", _("Closed")


class Gender(models.TextChoices):
    MALE = "MALE", _("Male")
    FEMALE = "FEMALE", _("Female")


class AddressType(models.TextChoices):
    BILLING = "BILLING", _("Billing")
    SHIPPING = "SHIPPING", _("Shipping")


class CodeStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    DEACTIVATED = "DEACTIVATED", _("Deactivated")

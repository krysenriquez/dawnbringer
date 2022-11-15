from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountStatus(models.TextChoices):
    DRAFT = "Draft", _("Draft")
    PENDING = "Pending", _("Pending")
    ACTIVE = "Active", _("Active")
    DEACTIVATED = "Deactivated", _("Deactivated")
    CLOSED = "Closed", _("Closed")

class Gender(models.TextChoices):
    MALE = "Male", _("Male")
    FEMALE = "Female", _("Female")

class CodeStatus(models.TextChoices):
    ACTIVE = "Active", _("Active")
    DEACTIVATED = "Deactivated", _("Deactivated")


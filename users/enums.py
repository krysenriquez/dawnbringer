from django.db import models
from django.utils.translation import gettext_lazy as _


class UserType(models.TextChoices):
    DEVELOPER = "DEVELOPER", _("Developer")
    STAFF = "STAFF", _("Staff")
    ADMIN = "ADMIN", _("Admin")
    MEMBER = "MEMBER", _("Member")

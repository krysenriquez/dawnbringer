from django.db import models
from django.utils.translation import gettext_lazy as _


class UserType(models.TextChoices):
    DEVELOPER = "Developer", _("Developer")
    ADMIN = "Admin", _("Admin")
    AUDITOR = "Auditor", _("Admin")
    STAFF = "Staff", _("Staff")
    MEMBER = "Member", _("Member")


class ActionType(models.TextChoices):
    CREATE = "CREATE", _("Create")
    RETRIEVE = "RETRIEVE", _("Retrieve")
    UPDATE = "UPDATE", _("Update")
    DELETE = "DELETE", _("Delete")

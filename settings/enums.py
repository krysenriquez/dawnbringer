from django.db import models
from django.utils.translation import gettext_lazy as _


class Settings(models.TextChoices):
    (None, "--------")
    QUANTITY_PER_DELIVERY = "QUANTITY_PER_DELIVERY", _("Quantity per Delivery")
    CODE_LENGTH = "CODE_LENGTH", _("Code Length")

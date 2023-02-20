from django.db import models
from django.utils.translation import gettext_lazy as _


class Settings(models.TextChoices):
    (None, "--------")
    QUANTITY_PER_DELIVERY = "QUANTITY_PER_DELIVERY", _("Quantity per Delivery")
    CODE_LENGTH = "CODE_LENGTH", _("Code Length")
    REGISTRATION_TAG = "REGISTRATION_TAG", _("Registration Tag")
    REGISTRATION_LINK = "REGISTRATION_LINK", _("Registration Link")
    SHOP_ORDER_LINK = "SHOP_ORDER_LINK", _("Shop Order Link")
    SHOP_CODE_LINK = "SHOP_CODE_LINK", _("Shop Code Link")
    POINT_CONVERSION_RATE = "POINT_CONVERSION_RATE", _("Point Conversion Rate")

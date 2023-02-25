from django.db import models
from django.utils.translation import gettext_lazy as _


class DeliveryType(models.TextChoices):
    FREE_DELIVERY = "FREE_DELIVERY", _("Free Delivery")
    EXPEDITED_DELIVERY = "EXPEDITED_DELIVERY", _("Expedited Delivery")
    REGULAR_SHIPPING = 'REGULAR_SHIPPING', _("Regular Shipping")


from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    ACTIVE = "ACTIVE", _("Active")
    INACTIVE = "INACTIVE", _("Inactive")


class AddressType(models.TextChoices):
    BILLING = "BILLING", _("Billing")
    SHIPPING = "SHIPPING", _("Shipping")


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    AWAITING_DELIVERY = "AWAITING_DELIVERY", _("Awaiting Delivery")
    AWAITING_PICKUP = "AWAITING_PICKUP", _("Awaiting Pickup")
    ON_DELIVERY = "ON_DELIVERY", _("On Delivery")
    CANCELLED = "CANCELLED", _("Cancelled")
    COMPLETED = "COMPLETED", _("Completed")
    REFUNDED = "REFUNDED", _("Refunded")


class OrderType(models.TextChoices):
    PICKUP = "PICKUP", _("Pickup")
    DELIVERY = "DELIVERY", _("Delivery")


class PaymentMethods(models.TextChoices):
    CASH = "CASH", _("Cash")
    CARD = "CARD", _("Card")
    BANK_TRANSFER = "BANK_TRANSFER", _("Bank Transfer")

from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    ACTIVE = "ACTIVE", _("Active")
    INACTIVE = "INACTIVE", _("Inactive")


class SupplyStatus(models.TextChoices):
    CANCELLED = "CANCELLED", _(
        "Cancelled"
    )  # -- Order has been cancelled by branch requestor. Can only cancel Pending Status.
    PENDING = "PENDING", _("Pending")  # -- Order has been made but not yet approved
    ORDER_RECEIVED = "ORDER_RECEIVED", _("Received")  # -- Order has been received by branch supplier
    BACK_ORDERED = "BACK_ORDERED", _(
        "Back Ordered"
    )  # --  Order has been received but currently no stocks on branch supplier
    PREPARING = "PREPARING", _("Preparing")  # -- Order has been received and preparing for transit
    IN_TRANSIT = "IN_TRANSIT", _("In Transit")  # -- Order in transit to branch requestor
    DELIVERED = "DELIVERED", _("Delivered")  # -- Order has been delivered to branch requestor
    DENIED = "DENIED", _("Denied")  # -- Order has been denied to branch supplier

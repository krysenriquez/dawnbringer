from django.db import models
from django.utils.translation import gettext_lazy as _


class Settings(models.TextChoices):
    (None, "--------")
    QUANTITY_PER_DELIVERY = "QUANTITY_PER_DELIVERY", _("Quantity per Delivery")
    CODE_LENGTH = "CODE_LENGTH", _("Code Length")
    REGISTRATION_TAG = "REGISTRATION_TAG", _("Registration Tag")
    REGISTRATION_LINK = "REGISTRATION_LINK", _("Registration Link")
    SHOP_DOMAIN = "SHOP_DOMAIN", _("Shop Domain")
    SHOP_ORDER_LINK = "SHOP_ORDER_LINK", _("Shop Order Link")
    SHOP_CODE_LINK = "SHOP_CODE_LINK", _("Shop Code Link")
    API_DOMAIN = "API_DOMAIN", _("Api Domain")
    MEMBER_DOMAIN = "MEMBER_DOMAIN", _("Member Domain")
    ADMIN_DOMAIN = "ADMIN_DOMAIN", _("Admin Domain")
    POINT_CONVERSION_RATE = "POINT_CONVERSION_RATE", _("Point Conversion Rate")
    MINIMUM_CONVERSTION_AMOUNT = "MINIMUM_CONVERSTION_AMOUNT", _("Minimum Conversion Amount")
    M_WALLET_CASHOUT_DAY = "M_WALLET_CASHOUT_DAY", _("Member Wallet Cashout Day")
    M_WALLET_CASHOUT_OVERRIDE = "M_WALLET_CASHOUT_OVERRIDE", _("Member Wallet Cashout Override")
    M_WALLET_MINIMUM_CASHOUT_AMOUNT = "M_WALLET_MINIMUM_CASHOUT_AMOUNT", _("Member Wallet Minimum Cashout Amount")
    CASHOUT_PROCESSING_FEE_PERCENTAGE = "CASHOUT_PROCESSING_FEE_PERCENTAGE", _("Cashout Processing Fee Percentage")
    RESET_PASSWORD_LINK = "RESET_PASSWORD_LINK", _("Reset Password Link")


class WalletType(models.TextChoices):
    C_WALLET = "C_WALLET", _("Company Wallet")
    M_WALLET = "M_WALLET", _("Member Wallet")
    PV_WALLET = "PV_WALLET", _("Point Value Wallet")


class ActivityStatus(models.TextChoices):
    REQUESTED = "REQUESTED", _("Requested")
    APPROVED = "APPROVED", _("Approved")
    RELEASED = "RELEASED", _("Released")
    DENIED = "DENIED", _("Denied")
    DONE = "DONE", _("Done")


class ActivityType(models.TextChoices):
    # * --- C Wallet
    PURCHASE = "PURCHASE", _("Purchase")  # * Foreign Key to Order
    PAYOUT = "PAYOUT", _("Payout")  # * Foreign Key to Cashout
    CASHOUT_PROCESSING_FEE = "CASHOUT_PROCESSING_FEE", _("Processing Fee")  # * Foreign Key to Cashout
    # * --- M_WALLET
    CASHOUT = "CASHOUT", _("Cashout")  # * No Foreign Key to Cashout Method
    POINT_CONVERSION = "POINT_CONVERSION", _("Point Conversion")  # * No Foreign Key
    REFERRAL_LINK_USAGE = "REFERRAL_LINK_USAGE", _("Referral Link Usage")  # * Foreign Key to Order

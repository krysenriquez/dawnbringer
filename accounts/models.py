import uuid
from django.db import models
from django.db.models import Sum, Max, F, Prefetch, Q
from django.db.models.functions import Coalesce
from simple_history.models import HistoricalRecords
from accounts.enums import AccountStatus, AddressType, CodeStatus, Gender
from core.enums import ActivityType


def account_avatar_directory(instance, filename):
    return "accounts/{0}/avatar/{1}".format(instance.account.account_id, filename)


def account_code_directory(instance, filename):
    return "accounts/{0}/code/{1}".format(instance.account.account_id, filename)


class Registration(models.Model):
    registration_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="registration")
    registration_status = models.CharField(
        max_length=11,
        choices=AccountStatus.choices,
        default=AccountStatus.PENDING,
    )

    def __str__(self):
        return "%s" % (self.order)


class Account(models.Model):
    account_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    referrer = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    last_name = models.CharField(max_length=255, null=True, blank=True)
    account_status = models.CharField(
        max_length=11,
        choices=AccountStatus.choices,
        default=AccountStatus.DRAFT,
    )
    user = models.OneToOneField(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="user",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_account",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_account",
        null=True,
        blank=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modifiedaccount",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()
    deleted = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-created", "-id"]

    def get_full_name(self):
        strings = [self.first_name, self.middle_name, self.last_name]
        return " ".join(filter(None, strings))

    def get_account_name(self):
        strings = [self.first_name, self.last_name]
        return " ".join(filter(None, strings))

    def get_account_number(self):
        return str(self.id).zfill(5)

    def get_all_children(self, children=None):
        if children is None:
            children = []
        for account in self.children.all():
            children.append(account)
            account.get_all_children(children)
        return children

    def get_all_referrers(self, referrers=None):
        if referrers is None:
            referrers = []
        if self.referrer:
            referrers.append(self.referrer)
            self.referrer.get_all_referrers(referrers)
        return referrers

    def get_four_level_referrers(self, referrers=None, level=None):
        if referrers is None:
            referrers = []
            level = 1
            referrers.append(
                {
                    "account": self,
                    "level": level,
                }
            )
        if self.referrer:
            level = level + 1
            if level > 4:
                return referrers

            referrers.append(
                {
                    "account": self.referrer,
                    "level": level,
                }
            )

            self.referrer.get_four_level_referrers(referrers, level)
        return referrers

    def get_membership_level_points(self, membership_level=None):
        return (
            self.activities.filter(membership_level=membership_level, activity_type=ActivityType.REFERRAL_LINK_USAGE)
            .aggregate(total=Coalesce(Sum("activity_amount"), 0, output_field=models.DecimalField()))
            .get("total")
        )

    def get_level_from_code(self, code_owner=None, account=None):

        pass

    def __str__(self):
        return "%s" % (self.get_full_name())


class PersonalInfo(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="personal_info")
    birthdate = models.DateField(
        blank=True,
        null=True,
    )
    gender = models.CharField(max_length=6, choices=Gender.choices, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_personal_info",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s" % (self.account)


class ContactInfo(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="contact_info")
    contact_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_contact_info",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s : %s" % (
            self.account,
            self.contact_number,
        )


class AvatarInfo(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="avatar_info")
    avatar = models.ImageField(blank=True, upload_to=account_avatar_directory)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_avatar_info",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s : %s" % (
            self.account,
            self.avatar,
        )


class Code(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, null=True, blank=True, related_name="code")
    code = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=32, choices=CodeStatus.choices, default=CodeStatus.ACTIVE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_code",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s :  %s - %s" % (
            self.account,
            self.code,
            self.status,
        )

    def activate_deactivate(self):
        if self.status == CodeStatus.ACTIVE:
            self.status = CodeStatus.DEACTIVATED
            self.save()
            return True

        if self.status == CodeStatus.DEACTIVATED:
            self.status = CodeStatus.ACTIVE
            self.save()
            return True

        return False


class AddressInfo(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="address_info")
    label = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    address1 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    address2 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    zip = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    province = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    address_type = models.CharField(
        max_length=11,
        choices=AddressType.choices,
        default=AddressType.SHIPPING,
    )
    is_default = models.BooleanField(
        default=False,
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_address_info",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s : %s" % (
            self.account,
            self.address_type,
        )

    class Meta:
        ordering = ["-is_default", "-id"]
        constraints = [
            models.UniqueConstraint(fields=("account",), condition=Q(is_default=True), name="one_default_per_account")
        ]


class CashoutMethod(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="cashout_methods")
    account_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    method = models.ForeignKey(
        "core.CashoutMethods", on_delete=models.CASCADE, related_name="cashout_methods", null=True, blank=True
    )
    other = models.CharField(max_length=255, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_cashout_method",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s : %s - %s %s" % (self.account, self.account_name, self.account_number, self.method)

    def get_cashout_method(self):
        return "%s - %s" % (self.method.method_name, self.account_number)

    def get_cashout_method_name(self):
        return "%s" % (self.method.method_name)

import uuid
from django.db import models
from accounts.enums import AccountStatus, AddressType, CodeStatus, Gender


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
    modified = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-created", "-id"]

    def get_full_name(self):
        return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)

    def get_account_name(self):
        return "%s %s" % (self.first_name, self.last_name)

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
            if level >= 4:
                return referrers

            referrers.append(
                {
                    "account": self.referrer,
                    "level": level,
                }
            )

            self.referrer.get_four_level_referrers(referrers, level)
        return referrers

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

    def __str__(self):
        return "%s" % (self.account)


class ContactInfo(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="contact_info")
    contact_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s : %s" % (
            self.account,
            self.contact_number,
        )


class AddressInfo(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="address_info")
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
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s : %s" % (
            self.account,
            self.address_type,
        )


class AvatarInfo(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="avatar_info")
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_attachment = models.ImageField(blank=True, upload_to=account_avatar_directory)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s : %s - %s" % (
            self.account,
            self.file_attachment,
            self.file_name,
        )


class Code(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, null=True, blank=True, related_name="code")
    code = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=32, choices=CodeStatus.choices, default=CodeStatus.ACTIVE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s :  %s - %s" % (
            self.account,
            self.code,
            self.status,
        )


class CashoutMethod(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="cashout_methods")
    account_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    method = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "%s : %s - %s %s" % (self.account, self.account_name, self.account_number, self.method)

    def get_method_name(self):
        return "%s - %s" % (self.method, self.account_number)

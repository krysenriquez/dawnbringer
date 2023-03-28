import uuid
import datetime
from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
)
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from users.enums import ActionType


def user_avatar_directory(instance, filename):
    return "users/{0}/avatar/{1}".format(instance.user_id, filename)


class UserManager(BaseUserManager):
    def _create_user(self, username, email_address, password, **extra_fields):
        if not email_address and not username:
            raise ValueError("A username or email is required to create an account")

        email_address = self.normalize_email(email_address)
        username = self.model.normalize_username(username)

        user = self.model(username=username, email_address=email_address, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email_address, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        email_address = self.normalize_email(email_address)
        username = self.model.normalize_username(username)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(username, email_address, password, **extra_fields)

    def create_staffuser(self, username, email_address, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        email_address = self.normalize_email(email_address)
        username = self.model.normalize_username(username)

        return self._create_user(username, email_address, password, **extra_fields)

    def create_memberuser(self, username, email_address, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        email_address = self.normalize_email(email_address)
        username = self.model.normalize_username(username)

        return self._create_user(username, email_address, password, **extra_fields)


class UserType(models.Model):
    user_type_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_type_name = models.CharField(
        max_length=255,
    )

    def get_all_users_count(self):
        return self.users.all().count()

    def __str__(self):
        return "%s" % (self.user_type_name)


class Module(models.Model):
    module_name = models.CharField(
        max_length=255,
    )

    def __str__(self):
        return "%s" % (self.module_name)


class Permission(models.Model):
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, related_name="permissions")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="permissions")
    can_create = models.BooleanField(default=False)
    can_retrieve = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)

    def __str__(self):
        return "%s: %s" % (self.user_type, self.module)


class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(
        unique=True,
        max_length=30,
    )
    display_name = models.CharField(max_length=50, blank=True, null=True)
    email_address = models.EmailField(
        verbose_name="email address",
        max_length=50,
        unique=True,
    )
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, related_name="users", blank=True, null=True)
    avatar = models.ImageField(blank=True, upload_to=user_avatar_directory)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="created_user",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="modified_user",
        null=True,
    )
    history = HistoricalRecords()
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "email_address",
    ]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        if not self.username:
            return "%s" % (self.email_address)
        else:
            return "%s" % (self.username)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_all_user_accounts(self):
        accounts = []
        for account in self.account_user.all():
            accounts.append(account)
        return accounts

    def get_last_seen(self, obj):
        last_seen = cache.get("seen_%s" % obj.username)
        obj.last_seen = last_seen
        return last_seen

    def get_online(self, obj):
        if obj.last_seen:
            now = datetime.datetime.now()
            delta = datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
            if now > obj.last_seen + delta:
                return False
            else:
                return True
        else:
            return False


class UserLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_logs")
    action_type = models.CharField(
        max_length=10,
        choices=ActionType.choices,
        default=ActionType.CREATE,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="user_logs_content_type",
        blank=True,
        null=True,
    )
    object_id = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )
    object_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    object_uuid = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    value_to_display = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return "%s - %s %s %s" % (
            self.user,
            self.action_type,
            self.content_type,
            self.object_id,
        )


class LogDetails(models.Model):
    user_logs = models.ForeignKey(
        UserLogs,
        on_delete=models.CASCADE,
        related_name="log_details",
        blank=True,
        null=True,
    )
    action = models.CharField(
        max_length=255,
    )

    def __str__(self):
        return "%s - %s" % (self.user_logs, self.action)

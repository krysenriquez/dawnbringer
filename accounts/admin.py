from django.contrib import admin
from dawnbringer.accounts.models import *


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "middle_name",
        "last_name",
        "account_status",
        "user",
        "parent",
        "referrer",
        "activation_code",
        "created",
    )

    search_fields = ("=id",)

    class Meta:
        model = Account
        verbose_name_plural = "Accounts"


class CodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "code_type",
        "status",
        "account",
        "created_by",
        "created",
        "modified",
    )
    search_fields = ("account",)
    list_filter = ("code_type",)
    ordering = (
        "modified",
        "created",
    )

    class Meta:
        model = Code
        verbose_name_plural = "Codes"


admin.site.register(Account, AccountAdmin)
admin.site.register(PersonalInfo)
admin.site.register(ContactInfo)
admin.site.register(AddressInfo)
admin.site.register(AvatarInfo)
admin.site.register(Code, CodeAdmin)

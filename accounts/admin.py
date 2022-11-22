from django.contrib import admin
from accounts.models import Account, PersonalInfo, ContactInfo, AddressInfo, AvatarInfo, Code


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "middle_name",
        "last_name",
        "account_status",
        "user",
        "parent",
        "created",
    )

    search_fields = ("=id",)

    class Meta:
        model = Account
        verbose_name_plural = "Accounts"


class CodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "status",
        "account",
        "created_by",
        "created",
        "modified",
    )
    search_fields = ("account",)
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

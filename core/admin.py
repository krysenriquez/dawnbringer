from django.contrib import admin
from core.models import Setting, MembershipLevel, Activity, ActivityDetails, CashoutMethods


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("activity_type", "account", "activity_amount", "wallet", "created", "modified")
    search_fields = ("account__id",)
    list_filter = ("activity_type", "wallet")
    ordering = ("-modified",)

    class Meta:
        model = Activity
        verbose_name_plural = "Activities"


admin.site.register(Setting)
admin.site.register(MembershipLevel)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityDetails)
admin.site.register(CashoutMethods)

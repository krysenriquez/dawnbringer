from django.contrib import admin
from core.models import Setting, MembershipLevel, Activity, ActivityDetails

admin.site.register(Setting)
admin.site.register(MembershipLevel)
admin.site.register(Activity)
admin.site.register(ActivityDetails)

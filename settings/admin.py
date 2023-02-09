from django.contrib import admin
from settings.models import Setting, MembershipLevel, Branch, DeliveryArea, BranchAssignment, Company

admin.site.register(Setting)
admin.site.register(MembershipLevel)
admin.site.register(Branch)
admin.site.register(BranchAssignment)
admin.site.register(DeliveryArea)
admin.site.register(Company)

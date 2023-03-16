from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from settings.models import Branch, DeliveryArea, BranchAssignment, Company

admin.site.register(Branch, SimpleHistoryAdmin)
admin.site.register(BranchAssignment, SimpleHistoryAdmin)
admin.site.register(DeliveryArea, SimpleHistoryAdmin)
admin.site.register(Company, SimpleHistoryAdmin)

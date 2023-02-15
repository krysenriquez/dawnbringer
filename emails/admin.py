from django.contrib import admin
from emails.models import EmailAddress, EmailTemplates

admin.site.register(EmailTemplates)
admin.site.register(EmailAddress)

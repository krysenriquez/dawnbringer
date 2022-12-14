from django_cron import CronJobBase, Schedule
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


class ClearBlacklistedTokensCronJob(CronJobBase):
    BlacklistedToken.objects.all().delete()

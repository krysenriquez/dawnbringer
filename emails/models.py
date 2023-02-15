from django.db import models


class EmailTemplates(models.Model):
    template = models.CharField(max_length=255, null=True, blank=True)
    subject = models.TextField(
        blank=True,
        null=True,
    )
    body = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return "%s" % (self.template)


class EmailAddress(models.Model):
    server_host = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    server_port = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    server_host_user = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    server_host_password = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    server_use_tls = models.BooleanField(
        default=False,
    )
    server_use_ssl = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return "%s" % (self.server_host_user)

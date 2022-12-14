from django.db import models
from settings.enums import Property


class Setting(models.Model):
    property = models.CharField(max_length=255, default=None, choices=Property.choices)
    value = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)

    class Meta:
        ordering = ["property"]

    def __str__(self):
        return "%s - %s" % (self.property, self.value)


class MembershipLevel(models.Model):
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    level = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return "%s - %s" % (self.name, self.level)


class EmailTemplate(models.Model):
    template_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    template = models.TextField(
        blank=True,
        null=True,
    )

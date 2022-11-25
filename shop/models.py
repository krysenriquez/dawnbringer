from django.db import models


class PageContent(models.Model):
    internal_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    page_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    page_slug = models.SlugField(
        max_length=255,
        blank=True,
        null=True,
    )
    page_content = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    is_home = models.BooleanField(default=False)
    meta_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    meta_robots = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    other_meta_data = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s : %s" % (self.internal_name, self.page_title, self.is_published)


class PageComponent(models.Model):
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    content = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s : %s" % (self.name, self.is_published)

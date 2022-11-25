from django.db import models


class PageContent(models.Model):
    internalName = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    pageTitle = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    pageSlug = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    pageContent = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    isHome = models.BooleanField(default=False)
    metaDescription = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    metaRobots = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    metaKeywords = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    otherMetaData = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    isPublished = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)


    def __str__(self):
        return "%s - %s : %s" % (self.internalName, self.pageTitle, self.isPublished)


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
    isPublished = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s : %s" % (self.name, self.isPublished)

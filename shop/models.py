import uuid
from django.db import models
from simple_history.models import HistoricalRecords


def component_attachments_directory(instance, filename):
    return "section-components/{0}/background/{1}".format(instance.id, filename)


class PageContent(models.Model):
    page_content_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_page_content",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_page_content",
        null=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s - %s : %s" % (self.internal_name, self.page_title, self.is_published)


class PageComponent(models.Model):
    page_component_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    page_content = models.ForeignKey(
        PageContent,
        related_name="page_component",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_page_component",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_page_component",
        null=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s : %s" % (self.name, self.is_published)


class SectionComponent(models.Model):
    section_component_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    page_component = models.ForeignKey(
        PageComponent,
        related_name="section_component",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    sub_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    description_1 = models.TextField(
        blank=True,
        null=True,
    )
    description_2 = models.TextField(
        blank=True,
        null=True,
    )
    description_3 = models.TextField(
        blank=True,
        null=True,
    )
    promo_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    button_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    button_link = models.TextField(
        max_length=255,
        blank=True,
        null=True,
    )
    image = models.ImageField(blank=True, upload_to=component_attachments_directory)
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_section_component",
        null=True,
    )
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="modified_section_component",
        null=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%s : %s" % (self.name, self.is_published)

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from shop.models import PageComponent, PageContent


class PageContentsSerializer(ModelSerializer):
    internalName = serializers.CharField(source="internal_name")
    pageTitle = serializers.CharField(source="page_title")
    pageSlug = serializers.CharField(source="page_slug")
    pageContent = serializers.CharField(source="page_content")
    isHome = serializers.CharField(source="is_home")
    metaDescription = serializers.CharField(source="meta_description")
    metaRobots = serializers.CharField(source="meta_robots")
    metaKeywords = serializers.CharField(source="meta_keywords")
    otherMetaData = serializers.CharField(source="other_meta_data")
    isPublished = serializers.CharField(source="is_published")
    isDeleted = serializers.CharField(source="is_deleted")

    class Meta:
        model = PageContent
        fields = [
            "internalName",
            "pageTitle",
            "pageSlug",
            "pageContent",
            "isHome",
            "metaDescription",
            "metaRobots",
            "metaKeywords",
            "otherMetaData",
            "isPublished",
            "isDeleted",
        ]


class PageComponentsSerializer(ModelSerializer):
    name = serializers.CharField()
    content = serializers.CharField()
    isPublished = serializers.CharField(source="is_published")
    isDeleted = serializers.CharField(source="is_deleted")

    class Meta:
        model = PageComponent
        fields = [
            "name",
            "content",
            "isPublished",
            "isDeleted",
        ]

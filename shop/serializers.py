from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from shop.models import PageComponent, PageContent, SectionComponent


class PageContentsListSerializer(ModelSerializer):
    class Meta:
        model = PageContent
        fields = [
            "internal_name",
            "page_title",
            "page_slug",
            "is_published",
        ]


class PageContentInfoSerializer(ModelSerializer):
    class Meta:
        model = PageContent
        fields = [
            "internal_name",
            "page_title",
            "page_slug",
            "page_content",
            "is_home",
            "meta_description",
            "meta_robots",
            "meta_keywords",
            "other_meta_data",
            "is_published",
        ]


class PageComponentsListSerializer(ModelSerializer):
    class Meta:
        model = PageComponent
        fields = [
            "name",
            "content",
            "is_published",
            "is_deleted",
        ]


class PageComponentInfoSerializer(ModelSerializer):
    class Meta:
        model = PageComponent
        fields = [
            "name",
            "content",
            "is_published",
            "is_deleted",
        ]


class SectionComponentsListSerializer(ModelSerializer):
    class Meta:
        model = SectionComponent
        fields = [
            "name",
            "header",
            "sub_header",
            "is_published",
        ]


class SectionComponentInfoSerializer(ModelSerializer):
    class Meta:
        model = SectionComponent
        fields = [
            "name",
            "header",
            "sub_header",
            "promo_text",
            "button_text",
            "button_link",
            "background_image",
            "is_published",
        ]


# Front End
class ShopPageContentsSerializer(ModelSerializer):
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


class ShopPageComponentsSerializer(ModelSerializer):
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


class ShopSectionComponentsSerializer(ModelSerializer):
    subHeader = serializers.CharField(source="sub_header")
    promoText = serializers.CharField(source="promo_text")
    buttonText = serializers.CharField(source="button_text")
    buttonLink = serializers.CharField(source="button_link")
    backgroundImage = serializers.ImageField(source="background_image")
    isPublished = serializers.CharField(source="is_published")
    isDeleted = serializers.CharField(source="is_deleted")

    class Meta:
        model = SectionComponent
        fields = [
            "name",
            "header",
            "subHeader",
            "promoText",
            "buttonText",
            "buttonLink",
            "backgroundImage",
            "isPublished",
            "isDeleted",
        ]

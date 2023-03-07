from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from shop.models import PageComponent, PageContent, SectionComponent


class SectionComponentsListSerializer(ModelSerializer):
    class Meta:
        model = SectionComponent
        fields = [
            "name",
            "title",
            "sub_title",
            "is_published",
        ]


class SectionComponentInfoSerializer(ModelSerializer):
    class Meta:
        model = SectionComponent
        fields = [
            "title",
            "sub_title",
            "description_1",
            "description_2",
            "description_3",
            "promo_text",
            "button_text",
            "button_link",
            "image",
            "is_published",
        ]


class PageComponentsListSerializer(ModelSerializer):
    class Meta:
        model = PageComponent
        fields = [
            "name",
            "is_published",
            "is_deleted",
        ]


class PageComponentInfoSerializer(ModelSerializer):
    class Meta:
        model = PageComponent
        fields = [
            "name",
            "is_published",
            "is_deleted",
        ]


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
            "is_home",
            "meta_description",
            "meta_robots",
            "meta_keywords",
            "other_meta_data",
            "is_published",
        ]


# Front End
class ShopSectionComponentsSerializer(ModelSerializer):
    subTitle = serializers.CharField(source="sub_title")
    description1 = serializers.CharField(source="description_1")
    description2 = serializers.CharField(source="description_2")
    description3 = serializers.CharField(source="description_3")
    promoText = serializers.CharField(source="promo_text")
    buttonText = serializers.CharField(source="button_text")
    buttonLink = serializers.CharField(source="button_link")

    class Meta:
        model = SectionComponent
        fields = [
            "title",
            "subTitle",
            "description1",
            "description2",
            "description3",
            "promoText",
            "buttonText",
            "buttonLink",
            "image",
        ]


class ShopPageComponentsSerializer(ModelSerializer):
    section_component = ShopSectionComponentsSerializer(many=True, required=False)
    isPublished = serializers.CharField(source="is_published")
    isDeleted = serializers.CharField(source="is_deleted")

    class Meta:
        model = PageComponent
        fields = [
            "name",
            "isPublished",
            "isDeleted",
            "section_component",
        ]


class ShopPageContentsSerializer(ModelSerializer):
    page_component = ShopPageComponentsSerializer(many=True, required=False)
    internalName = serializers.CharField(source="internal_name")
    pageTitle = serializers.CharField(source="page_title")
    pageSlug = serializers.CharField(source="page_slug")
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
            "isHome",
            "metaDescription",
            "metaRobots",
            "metaKeywords",
            "otherMetaData",
            "isPublished",
            "isDeleted",
            "page_component",
        ]

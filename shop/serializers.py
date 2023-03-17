from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from shop.models import PageComponent, PageContent, SectionComponent


class HistoricalRecordField(serializers.ListField):
    def to_representation(self, instance):
        histories = instance.all()
        old_record = None
        historical_data = []
        for history in histories.iterator():
            data = {}
            changes = []
            if old_record is None:
                old_record = history
            else:
                delta = old_record.diff_against(history)
                for change in delta.changes:
                    changes.append(
                        "{} changed from {} to {}".format(
                            change.field, change.old if change.old else "None", change.new if change.new else "None"
                        )
                    )
                old_record = history

            data["modified"] = history.modified
            if history.modified_by:
                data["modified_by"] = history.modified_by.username
            else:
                data["modified_by"] = None

            if len(changes) > 0:
                data["changes"] = changes
            else:
                data["changes"] = None

            historical_data.append(data)

        return super().to_representation(historical_data)


class PageContentsListSerializer(ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.display_name", required=False)

    class Meta:
        model = PageContent
        fields = [
            "id",
            "page_content_id",
            "internal_name",
            "page_title",
            "page_slug",
            "is_published",
            "created_by_name",
        ]


class PageContentInfoSerializer(ModelSerializer):
    history = HistoricalRecordField(read_only=True)

    class Meta:
        model = PageContent
        fields = [
            "page_content_id",
            "internal_name",
            "page_title",
            "page_slug",
            "is_home",
            "meta_description",
            "meta_robots",
            "meta_keywords",
            "other_meta_data",
            "is_published",
            "history",
        ]


class PageContentSerializer(ModelSerializer):
    def create(self, validated_data):
        page_content = PageContent.objects.create(**validated_data)

        return page_content

    def update(self, instance, validated_data):
        instance.internal_name = validated_data.get("internal_name", instance.internal_name)
        instance.page_title = validated_data.get("page_title", instance.page_title)
        instance.page_slug = validated_data.get("page_slug", instance.page_slug)
        instance.is_home = validated_data.get("is_home", instance.is_home)
        instance.meta_description = validated_data.get("meta_description", instance.meta_description)
        instance.meta_robots = validated_data.get("meta_robots", instance.meta_robots)
        instance.meta_keywords = validated_data.get("meta_keywords", instance.meta_keywords)
        instance.other_meta_data = validated_data.get("other_meta_data", instance.other_meta_data)
        instance.is_published = validated_data.get("is_published", instance.is_published)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.modified_by = self.context.get("request").user
        instance.save()

        return instance

    class Meta:
        model = PageContent
        fields = "__all__"


class PageComponentsListSerializer(ModelSerializer):
    page_content_name = serializers.CharField(source="page_content.internal_name", required=False)
    created_by_name = serializers.CharField(source="created_by.display_name", required=False)

    class Meta:
        model = PageComponent
        fields = [
            "id",
            "page_component_id",
            "page_content_name",
            "name",
            "is_published",
            "is_deleted",
            "created_by_name",
        ]


class PageComponentInfoSerializer(ModelSerializer):
    history = HistoricalRecordField(read_only=True)

    class Meta:
        model = PageComponent
        fields = ["page_content", "page_component_id", "name", "is_published", "is_deleted", "history"]


class PageComponentSerializer(ModelSerializer):
    def create(self, validated_data):
        page_component = PageComponent.objects.create(**validated_data)

        return page_component

    def update(self, instance, validated_data):
        instance.page_content = validated_data.get("page_content", instance.page_content)
        instance.name = validated_data.get("name", instance.name)
        instance.is_published = validated_data.get("is_published", instance.is_published)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.modified_by = self.context.get("request").user
        instance.save()

        return instance

    class Meta:
        model = PageComponent
        fields = "__all__"


class SectionComponentsListSerializer(ModelSerializer):
    page_component_name = serializers.CharField(source="page_component.name", required=False)
    created_by_name = serializers.CharField(source="created_by.display_name", required=False)

    class Meta:
        model = SectionComponent
        fields = [
            "section_component_id",
            "page_component_name",
            "name",
            "title",
            "sub_title",
            "is_published",
            "created_by_name",
        ]


class SectionComponentInfoSerializer(ModelSerializer):
    history = HistoricalRecordField(read_only=True)

    class Meta:
        model = SectionComponent
        fields = [
            "section_component_id",
            "page_component",
            "name",
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
            "is_deleted",
            "history",
        ]


class SectionComponentSerializer(ModelSerializer):
    def create(self, validated_data):
        section_component = SectionComponent.objects.create(**validated_data)

        return section_component

    def update(self, instance, validated_data):
        instance.page_component = validated_data.get("page_component", instance.page_component)
        instance.name = validated_data.get("name", instance.name)
        instance.title = validated_data.get("title", instance.title)
        instance.sub_title = validated_data.get("sub_title", instance.sub_title)
        instance.description_1 = validated_data.get("description_1", instance.description_1)
        instance.description_2 = validated_data.get("description_2", instance.description_2)
        instance.description_3 = validated_data.get("description_3", instance.description_3)
        instance.promo_text = validated_data.get("promo_text", instance.promo_text)
        instance.button_text = validated_data.get("button_text", instance.button_text)
        instance.button_link = validated_data.get("button_link", instance.button_link)
        instance.image = validated_data.get("image", instance.image)
        instance.is_published = validated_data.get("is_published", instance.is_published)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.modified_by = self.context.get("request").user
        instance.save()

        return instance

    class Meta:
        model = SectionComponent
        fields = "__all__"


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

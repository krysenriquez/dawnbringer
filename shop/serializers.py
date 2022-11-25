from rest_framework.serializers import ModelSerializer
from shop.models import PageComponent, PageContent


class PageComponentsSerializer(ModelSerializer):
    # = serializers.CharField(source='alternate_name')

    class Meta:
        model = PageComponent
        fields = "__all__"


class PageContentsSerializer(ModelSerializer):
    class Meta:
        model = PageContent
        fields = "__all__"

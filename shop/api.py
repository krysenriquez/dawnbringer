from rest_framework.viewsets import ModelViewSet
from shop.models import PageContent, PageComponent
from shop.serializers import PageComponentsSerializer, PageContentsSerializer


class PageContentsViewSet(ModelViewSet):
    queryset = PageContent.objects.all()
    serializer_class = PageContentsSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = PageContent.objects.exclude(is_deleted=True)
        return queryset
        # id = self.request.query_params.get("id", None)
        # queryset = PageContent.objects.exclude(is_deleted=False)
        # print(queryset)
        # if id:
        #     queryset = queryset.filter(id=id)

        # return queryset

class PageComponentsViewSet(ModelViewSet):
    queryset = PageComponent.objects.all()
    serializer_class = PageComponentsSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        # id = self.request.query_params.get("id", None)
        queryset = PageComponent.objects.exclude(is_deleted=True)
        print(queryset)
        return queryset
        # if id:
        #     queryset = queryset.filter(id=id)

        #  queryset

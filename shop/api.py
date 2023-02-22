from rest_framework.viewsets import ModelViewSet
from shop.models import PageContent, PageComponent, SectionComponent
from shop.serializers import PageComponentsSerializer, PageContentsSerializer, SectionComponentsSerializer
from vanguard.throttle import DevTestingAnonThrottle


class PageContentsViewSet(ModelViewSet):
    queryset = PageContent.objects.all()
    serializer_class = PageContentsSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        return PageContent.objects.exclude(is_deleted=True).filter(is_published=True)


class PageComponentsViewSet(ModelViewSet):
    queryset = PageComponent.objects.all()
    serializer_class = PageComponentsSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        return PageComponent.objects.exclude(is_deleted=True).filter(is_published=True)


class SectionComponentsViewSet(ModelViewSet):
    queryset = SectionComponent.objects.all()
    serializer_class = SectionComponentsSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        return SectionComponent.objects.exclude(is_deleted=True).filter(is_published=True)

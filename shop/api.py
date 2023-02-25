from rest_framework.viewsets import ModelViewSet
from shop.models import PageContent, PageComponent, SectionComponent
from shop.serializers import (
    PageContentsListSerializer,
    PageContentInfoSerializer,
    PageComponentsListSerializer,
    PageComponentInfoSerializer,
    SectionComponentsListSerializer,
    SectionComponentInfoSerializer,
    ShopPageComponentsSerializer,
    ShopPageContentsSerializer,
    ShopSectionComponentsSerializer,
)
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser
from vanguard.throttle import DevTestingAnonThrottle


class PageContentsListViewSet(ModelViewSet):
    queryset = PageContent.objects.all()
    serializer_class = PageContentsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return PageContent.objects.exclude(is_deleted=True)


class PageContentsInfoViewSet(ModelViewSet):
    queryset = PageContent.objects.all()
    serializer_class = PageContentInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        id = self.request.query_params.get("id", None)
        return PageContent.objects.exclude(is_deleted=True).filter(id=id)


class PageComponentsListViewSet(ModelViewSet):
    queryset = PageComponent.objects.all()
    serializer_class = PageComponentsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return PageComponent.objects.exclude(is_deleted=True)


class PageComponentsInfoViewSet(ModelViewSet):
    queryset = PageComponent.objects.all()
    serializer_class = PageComponentInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        id = self.request.query_params.get("id", None)
        return PageComponent.objects.exclude(is_deleted=True).filter(id=id)


class SectionComponentsListViewSet(ModelViewSet):
    queryset = SectionComponent.objects.all()
    serializer_class = SectionComponentsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return SectionComponent.objects.exclude(is_deleted=True)


class SectionComponentsInfoViewSet(ModelViewSet):
    queryset = SectionComponent.objects.all()
    serializer_class = SectionComponentInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        id = self.request.query_params.get("branch_id", None)
        return SectionComponent.objects.exclude(is_deleted=True).filter(id=id)


# Front End
class ShopPageContentsViewSet(ModelViewSet):
    queryset = PageContent.objects.all()
    serializer_class = ShopPageContentsSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        return PageContent.objects.exclude(is_deleted=True).filter(is_published=True)


class ShopPageComponentsViewSet(ModelViewSet):
    queryset = PageComponent.objects.all()
    serializer_class = ShopPageComponentsSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        return PageComponent.objects.exclude(is_deleted=True).filter(is_published=True)


class ShopSectionComponentsViewSet(ModelViewSet):
    queryset = SectionComponent.objects.all()
    serializer_class = ShopSectionComponentsSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        return SectionComponent.objects.exclude(is_deleted=True).filter(is_published=True)

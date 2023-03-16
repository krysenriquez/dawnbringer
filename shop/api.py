from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from shop.models import PageContent, PageComponent, SectionComponent
from shop.serializers import (
    PageContentsListSerializer,
    PageContentInfoSerializer,
    PageContentSerializer,
    PageComponentsListSerializer,
    PageComponentInfoSerializer,
    PageComponentSerializer,
    SectionComponentsListSerializer,
    SectionComponentInfoSerializer,
    SectionComponentSerializer,
    ShopPageContentsSerializer,
)
from shop.services import transform_form_data_to_json
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser
from vanguard.throttle import DevTestingAnonThrottle
from users.enums import ActionType
from users.services import create_user_logs
from logs.services import create_log


class PageContentsListViewSet(ModelViewSet):
    queryset = PageContent.objects.all()
    serializer_class = PageContentsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return PageContent.objects.exclude(is_deleted=True).order_by("-id")


class PageContentsInfoViewSet(ModelViewSet):
    queryset = PageContent.objects.all()
    serializer_class = PageContentInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        page_content_id = self.request.query_params.get("page_content_id", None)
        return PageContent.objects.exclude(is_deleted=True).filter(page_content_id=page_content_id)


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
        page_component_id = self.request.query_params.get("page_component_id", None)
        return PageComponent.objects.exclude(is_deleted=True).filter(page_component_id=page_component_id)


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
        section_component_id = self.request.query_params.get("section_component_id", None)
        return SectionComponent.objects.exclude(is_deleted=True).filter(section_component_id=section_component_id)


class CreatePageContentView(views.APIView):
    def post(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.pk
        request.data["modified_by"] = request.user.pk
        serializer = PageContentSerializer(data=request.data)
        if serializer.is_valid():
            created_page_content = serializer.save()
            create_log("INFO", "Created Page Content", created_page_content)
            create_user_logs(
                user=request.user,
                action_type=ActionType.CREATE,
                content_type_model="pagecontent",
                object_id=created_page_content.pk,
                object_type="Page Content",
                object_uuid=created_page_content.page_content_id,
                value_to_display="Created Page Content",
            )
            return Response(data={"detail": "Page Content created."}, status=status.HTTP_201_CREATED)
        else:
            create_log("ERROR", "Error Page Content Create", serializer.errors)
            return Response(
                data={"detail": "Unable to create Page Content."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdatePageContentView(views.APIView):
    def post(self, request, *args, **kwargs):
        page_content = PageContent.objects.get(page_content_id=request.data["page_content_id"])
        serializer = PageContentSerializer(page_content, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            updated_page_content = serializer.save()
            create_log("INFO", "Updated Page Content", updated_page_content)
            create_user_logs(
                user=request.user,
                action_type=ActionType.UPDATE,
                content_type_model="pagecontent",
                object_id=updated_page_content.pk,
                object_type="Page Content",
                object_uuid=updated_page_content.page_content_id,
                value_to_display="Updated Page Content",
            )
            return Response(data={"detail": "Page Content updated."}, status=status.HTTP_200_OK)
        else:
            create_log("ERROR", "Error Page Content Update", serializer.errors)
            return Response(
                data={"detail": "Unable to update Page Content."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreatePageComponentView(views.APIView):
    def post(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.pk
        request.data["modified_by"] = request.user.pk
        serializer = PageComponentSerializer(data=request.data)
        if serializer.is_valid():
            created_page_component = serializer.save()
            create_log("INFO", "Created Page Component", created_page_component)
            create_user_logs(
                user=request.user,
                action_type=ActionType.CREATE,
                content_type_model="pagecomponent",
                object_id=created_page_component.pk,
                object_type="Page Component",
                object_uuid=created_page_component.page_component_id,
                value_to_display="Created Page Component",
            )
            return Response(data={"detail": "Page Component created."}, status=status.HTTP_201_CREATED)
        else:
            create_log("ERROR", "Error Page Component Create", serializer.errors)
            return Response(
                data={"detail": "Unable to create Page Component."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdatePageComponentView(views.APIView):
    def post(self, request, *args, **kwargs):
        page_component = PageComponent.objects.get(page_component_id=request.data["page_component_id"])
        serializer = PageComponentSerializer(
            page_component, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            updated_page_component = serializer.save()
            create_log("INFO", "Updated Page Component", updated_page_component)
            create_user_logs(
                user=request.user,
                action_type=ActionType.UPDATE,
                content_type_model="pagecomponent",
                object_id=updated_page_component.pk,
                object_type="Page Component",
                object_uuid=updated_page_component.page_component_id,
                value_to_display="Updated Page Component",
            )
            return Response(data={"detail": "Page Component updated."}, status=status.HTTP_200_OK)
        else:
            create_log("ERROR", "Error Page Component Update", serializer.errors)
            return Response(
                data={"detail": "Unable to update Page Component."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateSectionComponentView(views.APIView):
    def post(self, request, *args, **kwargs):
        processed_request = transform_form_data_to_json(request.data)
        processed_request["created_by"] = request.user.pk
        processed_request["modified_by"] = request.user.pk
        serializer = SectionComponentSerializer(data=processed_request)
        if serializer.is_valid():
            created_section_component = serializer.save()
            create_log("INFO", "Created Section Component", created_section_component)
            create_user_logs(
                user=request.user,
                action_type=ActionType.CREATE,
                content_type_model="sectioncomponent",
                object_id=created_section_component.pk,
                object_type="Section Component",
                object_uuid=created_section_component.section_component_id,
                value_to_display="Created Section Component",
            )
            return Response(data={"detail": "Section Component created."}, status=status.HTTP_201_CREATED)
        else:
            create_log("ERROR", "Error Section Component Create", serializer.errors)
            return Response(
                data={"detail": "Unable to create Section Component."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateSectionComponentView(views.APIView):
    def post(self, request, *args, **kwargs):
        processed_request = transform_form_data_to_json(request.data)
        section_component = SectionComponent.objects.get(section_component_id=processed_request["section_component_id"])
        serializer = SectionComponentSerializer(
            section_component, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            updated_section_component = serializer.save()
            create_log("INFO", "Updated Section Component", updated_section_component)
            create_user_logs(
                user=request.user,
                action_type=ActionType.UPDATE,
                content_type_model="sectioncomponent",
                object_id=updated_section_component.pk,
                object_type="Section Component",
                object_uuid=updated_section_component.section_component_id,
                value_to_display="Updated Section Component",
            )
            return Response(data={"detail": "Section Component updated."}, status=status.HTTP_200_OK)
        else:
            create_log("ERROR", "Error Section Component Update", serializer.errors)
            return Response(
                data={"detail": "Unable to update Section Component."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Front End
class ShopPageContentsViewSet(ModelViewSet):
    queryset = PageContent.objects.all()
    serializer_class = ShopPageContentsSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        page_slug = self.request.query_params.get("page_slug", None)
        return PageContent.objects.exclude(is_deleted=True, is_published=False).filter(page_slug=page_slug)

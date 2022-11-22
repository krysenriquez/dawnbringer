from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser
from settings.models import Setting, MembershipLevel
from settings.serializers import SettingsSerializer, MembershipLevelsSerializer


# Viewsets
class SettingsViewSet(ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = (permissions.IsAuthenticated, IsDeveloperUser, IsAdminUser, IsStaffUser)
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Setting.objects.all().order_by("-property")

        return queryset


class MembershipLevelsViewSet(ModelViewSet):
    queryset = MembershipLevel.objects.all()
    serializer_class = MembershipLevelsSerializer
    permission_classes = (permissions.IsAuthenticated, IsDeveloperUser, IsAdminUser, IsStaffUser)
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = MembershipLevel.objects.all().order_by("-name")

        return queryset


# HTTP Methods
class UpdateSettingsView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, IsDeveloperUser, IsAdminUser, IsStaffUser)

    def post(self, request, *args, **kwargs):
        settings = request.data
        instances = []
        for setting in settings:
            obj = Setting.objects.get(property=setting["property"])
            if obj:
                obj.property = setting["property"]
                obj.value = setting["value"]
                obj.save()
                instances.append(obj)

        serializer = SettingsSerializer(instances, many=True)
        if serializer:
            return Response(data={"message": "System Settings Updated."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"message": "Unable to create Update System Settings."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateMembershipLevelsView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, IsDeveloperUser, IsAdminUser, IsStaffUser)

    def post(self, request, *args, **kwargs):
        membership_levels = request.data
        instances = []
        for membership_level in membership_levels:
            obj = MembershipLevel.objects.get(property=membership_level["name"])
            if obj:
                obj.name = membership_level["name"]
                obj.level = membership_level["level"]
                obj.save()
                instances.append(obj)

        serializer = MembershipLevelsSerializer(instances, many=True)
        if serializer:
            return Response(data={"message": "Membership Levels Updated."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"message": "Unable to create Update Membership Levels."},
                status=status.HTTP_400_BAD_REQUEST,
            )

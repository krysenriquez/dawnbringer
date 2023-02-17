from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from core.models import Setting, MembershipLevel
from core.serializers import SettingsSerializer, MembershipLevelsSerializer
from core.services import comp_plan
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser

from orders.models import Order


class SettingsViewSet(ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Setting.objects.all().order_by("-property")


class MembershipLevelsViewSet(ModelViewSet):
    queryset = MembershipLevel.objects.all()
    serializer_class = MembershipLevelsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return MembershipLevel.objects.all().order_by("level")


class UpdateSettingsView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

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
            return Response(data={"detail": "System Settings Updated."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"detail": "Unable to create Update System Settings."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateMembershipLevelsView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

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
            return Response(data={"detail": "Membership Levels Updated."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"detail": "Unable to create Update Membership Levels."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Test(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=request.data.get("order"))
        comp_plan(request, order)
        return Response(
            data={"detail": "test"},
            status=status.HTTP_200_OK,
        )

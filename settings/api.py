from django.db.models import Prefetch
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser
from settings.models import Branch, BranchAssignment, Setting, MembershipLevel
from settings.serializers import (
    BranchAssignmentsSerializer,
    BranchesSerializer,
    SettingsSerializer,
    MembershipLevelsSerializer,
)


# Viewsets
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


class BranchAssignmentsViewSet(ModelViewSet):
    queryset = BranchAssignment.objects.all()
    serializer_class = BranchAssignmentsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return BranchAssignment.objects.prefetch_related(
            Prefetch("branch", queryset=Branch.objects.order_by("id"))
        ).filter(user=self.request.user)


class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchesSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        return Branch.objects.all()


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
            return Response(data={"message": "System Settings Updated."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"message": "Unable to create Update System Settings."},
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
            return Response(data={"message": "Membership Levels Updated."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"message": "Unable to create Update Membership Levels."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Front End
class ShopBranchListViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchesSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        return Branch.objects.all()


class ShopBranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchesSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        if branch_id:
            return Branch.objects.filter(branch_id=branch_id).all()

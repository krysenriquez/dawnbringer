from django.db.models import Prefetch
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from settings.models import Branch, BranchAssignment
from settings.serializers import (
    BranchAssignmentsSerializer,
    BranchesSerializer,
)
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser


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

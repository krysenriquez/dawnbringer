from django.db.models import Prefetch
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from settings.models import Company, Branch, BranchAssignment
from settings.serializers import (
    CompanySerializer,
    BranchesListSerializer,
    BranchInfoSerializer,
    BranchAssignmentsSerializer,
    CreateBranchSerializer,
    ShopBranchSerializer,
    ShopDeliveryAreaSerializer,
)
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser
from vanguard.throttle import DevTestingAnonThrottle
from users.enums import ActionType
from users.services import create_user_logs


class BranchAssignmentsViewSet(ModelViewSet):
    queryset = BranchAssignment.objects.all()
    serializer_class = BranchAssignmentsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return BranchAssignment.objects.prefetch_related(
            Prefetch("branch", queryset=Branch.objects.order_by("id"))
        ).filter(user=self.request.user)


class BranchListViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchesListSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        return Branch.objects.all()


class BranchInfoViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchInfoSerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        return Branch.objects.filter(branch_id=branch_id)


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = []
    http_method_names = ["get"]

    def get_queryset(self):
        return Company.objects.filter(id=1)


class CreateBranchView(views.APIView):
    def post(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.pk
        request.data["modified_by"] = request.user.pk
        serializer = CreateBranchSerializer(data=request.data)
        if serializer.is_valid():
            created_branch = serializer.save()
            create_user_logs(
                user=request.user,
                action_type=ActionType.CREATE,
                content_type_model="branch",
                object_id=created_branch.pk,
                object_type="Branch",
                object_uuid=created_branch.branch_id,
                value_to_display="Created Branch",
            )
            return Response(data={"detail": "Branch created."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={"detail": "Unable to create Branch."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateBranchView(views.APIView):
    def post(self, request, *args, **kwargs):
        branch = Branch.objects.get(branch_id=request.data["branch_id"])
        serializer = CreateBranchSerializer(branch, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            updated_branch = serializer.save()
            create_user_logs(
                user=request.user,
                action_type=ActionType.UPDATE,
                content_type_model="branch",
                object_id=updated_branch.pk,
                object_type="Branch",
                object_uuid=updated_branch.branch_id,
                value_to_display="Updated Branch",
            )
            return Response(data={"detail": "Branch updated."}, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"detail": "Unable to update Branch."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ShopGetDeliveryAreaAmountView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        city = request.data.get("city")
        province = request.data.get("province")
        country = request.data.get("country")

        return Response(
            data={"amount": int(150)},
            status=status.HTTP_200_OK,
        )


# Front End
class ShopBranchListViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = ShopBranchSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        return Branch.objects.all()


class ShopBranchInfoViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = ShopBranchSerializer
    permission_classes = []
    http_method_names = ["get"]
    throttle_classes = [DevTestingAnonThrottle]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id", None)
        if branch_id:
            return Branch.objects.filter(branch_id=branch_id).all()

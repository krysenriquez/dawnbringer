from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from accounts.enums import AccountStatus
from accounts.models import Account
from accounts.serializers import (
    AccountSerializer,
    AccountProfileSerializer,
    AccountListSerializer,
)
from accounts.services import (
    activate_account_login,
    create_registration_link,
    get_registration_link_object,
    verify_registration_link,
    process_create_account_request,
    update_registration_status,
)
from users.enums import UserType
from users.services import create_new_user
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser


class AccountProfileViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountProfileSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            account_id = self.request.query_params.get("account_id", None)
            queryset = Account.objects.exclude(is_deleted=True).filter(account_id=account_id).all()
            if queryset.exists():
                return queryset


class AccountListViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        if self.request.user.user_type == UserType.ADMIN:
            queryset = Account.objects.exclude(is_deleted=True).all()
            if queryset.exists():
                return queryset
        else:
            return Account.objects.none()


class RegisterAccountView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        is_verified, registration = get_registration_link_object(request.data["data"])
        if is_verified:
            processed_request = process_create_account_request(request.data, registration)
            serializer = AccountSerializer(data=processed_request)
            if serializer.is_valid():
                new_member = serializer.save()
                if new_member:
                    activate_account_login(new_member, request.data["user"])
                    update_registration_status(registration)
                    return Response(data={"detail": "Account created."}, status=status.HTTP_201_CREATED)
                return Response(
                    data={"detail": "Unable to create Account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                print(serializer.errors)
                return Response(
                    data={"detail": "Unable to create Account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data={"detail": "Invalid Registration Link"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyRegistrationView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        is_verified, message = verify_registration_link(request.data["data"])
        if is_verified:
            return Response(
                data={"detail": message},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"detail": message},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyAccountView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        if request.user.user_type == UserType.ADMIN:
            account_id = request.data.get("account_id").lstrip("0")
            if account_id:
                try:
                    account = Account.objects.get(id=account_id)
                    return Response(
                        data={"detail": "Account existing."},
                        status=status.HTTP_200_OK,
                    )
                except Account.DoesNotExist:
                    return Response(
                        data={"detail": "Account does not exist."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                return Response(
                    data={"detail": "Account does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

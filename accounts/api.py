from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from accounts.models import Account
from accounts.serializers import (
    AccountSerializer,
    AccountProfileSerializer,
    AccountListSerializer,
)
from users.enums import UserType


class AccountProfileViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)
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
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get"]

    def get_queryset(self):
        if self.request.user.user_type == UserType.ADMIN:
            queryset = Account.objects.exclude(is_deleted=True).all()
            if queryset.exists():
                return queryset
        else:
            return Account.objects.none()


class CreateAccountView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = AccountSerializer(data=request.data)

        if serializer.is_valid():
            new_member = serializer.save()
            return Response(data={"message": "Account created."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(
                data={"message": "Unable to create Account."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyAccountView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if request.user.user_type == UserType.ADMIN:
            account_id = request.data.get("account_id").lstrip("0")
            if account_id:
                try:
                    account = Account.objects.get(id=account_id)
                    return Response(
                        data={"message": "Account existing."},
                        status=status.HTTP_200_OK,
                    )
                except Account.DoesNotExist:
                    return Response(
                        data={"message": "Account does not exist."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                return Response(
                    data={"message": "Account does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

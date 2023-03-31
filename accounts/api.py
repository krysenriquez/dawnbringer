from django.db.models import Prefetch
from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from logs.services import create_log
from accounts.enums import AccountStatus
from accounts.models import Account, AddressInfo, CashoutMethod
from accounts.serializers import (
    AccountUserSerializer,
    AddressInfoSerializer,
    CreateUpdateAddressInfoSerializer,
    AccountMemberInfoSerializer,
    AccountProfileInfoSerializer,
    CreateUpdateAccountSerializer,
    AccountInfoSerializer,
    AccountsListSerializer,
    CashoutMethodSerializer,
)
from accounts.services import (
    activate_account_login,
    attach_orders_to_registered_account,
    get_registration_link_object,
    transform_account_form_data_to_json,
    undefault_all_address_info,
    verify_code_details,
    verify_registration_link,
    process_create_account_request,
    update_registration_status,
)
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsMemberUser, IsStaffUser


class AddressMemberInfoViewSet(ModelViewSet):
    queryset = AddressInfo.objects.all()
    serializer_class = AddressInfoSerializer
    permission_classes = [IsMemberUser]

    def get_queryset(self):
        return AddressInfo.objects.filter(id=self.request.query_params.get("id"))


class AccountAdminListViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountsListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Account.objects.exclude(is_deleted=True).all()


class AccountAdminInfoViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        account_id = self.request.query_params.get("account_id", None)
        if account_id:
            return Account.objects.exclude(is_deleted=True).filter(account_id=account_id).all()


class AccountUserInfoAdminViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountUserSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        account_id = self.request.query_params.get("account_id", None)
        if account_id:
            return Account.objects.exclude(is_deleted=True).filter(account_id=account_id).all()


class AccountCashoutMethodsMemberViewSet(ModelViewSet):
    queryset = CashoutMethod.objects.all()
    serializer_class = CashoutMethodSerializer
    permission_classes = [IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = CashoutMethod.objects.filter(account__user=self.request.user).all()
        if queryset.exists():
            return queryset


class AccountMemberInfoViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountMemberInfoSerializer
    permission_classes = [IsMemberUser]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


class AccountProfileInfoViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountProfileInfoSerializer
    permission_classes = [IsMemberUser]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).prefetch_related(
            Prefetch("address_info", AddressInfo.objects.exclude(is_deleted=True))
        )


class RegisterAccountView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        is_verified, registration = get_registration_link_object(request.data["data"])
        if is_verified:
            processed_request = process_create_account_request(request.data, registration)
            serializer = CreateUpdateAccountSerializer(data=processed_request)
            if serializer.is_valid():
                new_member = serializer.save()
                create_log("INFO", "Created Account", new_member)
                if new_member:
                    activate_account_login(new_member, request.data["user"])
                    attach_orders_to_registered_account(new_member, registration)
                    update_registration_status(registration)
                    return Response(data={"detail": "Account created."}, status=status.HTTP_201_CREATED)
                return Response(
                    data={"detail": "Unable to create Account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                create_log("ERROR", "Error Account Create", serializer.errors)
                return Response(
                    data={"detail": "Unable to create Account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data={"detail": "Invalid Registration Link"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UpdateAccountMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        data = transform_account_form_data_to_json(request.data)
        account = Account.objects.get(user=request.user)
        serializer = CreateUpdateAccountSerializer(account, data=data, partial=True, context={"request": request})
        if serializer.is_valid():
            updated_member = serializer.save()
            create_log("INFO", "Updated Account (Admin)", updated_member)
            if updated_member:
                return Response(
                    data={"detail": "Profile updated"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                data={"detail": "Unable to update Profile"},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            create_log("ERROR", "Error Account Update (Admin)", serializer.errors)
            return Response(
                data={"detail": "Unable to update Profile"},
                status=status.HTTP_409_CONFLICT,
            )


class CreateAddressMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        account = Account.objects.get(user=request.user)
        if account:
            request.data["account"] = account.pk
            request.data["created_by"] = request.user.pk
            serializer = CreateUpdateAddressInfoSerializer(data=request.data)
            if serializer.is_valid():
                created_address = serializer.save()
                create_log("INFO", "Created Address", created_address)
                if created_address:
                    return Response(
                        data={"detail": "Address created"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    data={"detail": "Unable to create Address"},
                    status=status.HTTP_409_CONFLICT,
                )
            else:
                create_log("ERROR", "Error Address Create", serializer.errors)
                return Response(
                    data={"detail": "Unable to create Address"},
                    status=status.HTTP_409_CONFLICT,
                )
        else:
            create_log("ERROR", "Error Address Create: No Account linked to User", account)
            return Response(
                data={"detail": "Unable to create Address"},
                status=status.HTTP_409_CONFLICT,
            )


class UpdateAddressMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        address = AddressInfo.objects.get(id=request.data.get("id"))
        serializer = CreateUpdateAddressInfoSerializer(
            address, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            updated_address = serializer.save()
            create_log("INFO", "Updated Address", updated_address)
            if updated_address:
                return Response(
                    data={"detail": "Address updated"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                data={"detail": "Unable to update Address"},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            create_log("ERROR", "Error Address Update", serializer.errors)
            return Response(
                data={"detail": "Unable to update Address"},
                status=status.HTTP_409_CONFLICT,
            )


class UpdateDefaultAddressMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        undefaulted_addresses = undefault_all_address_info(self.request)
        if undefaulted_addresses:
            address = AddressInfo.objects.get(id=request.data.get("id"))
            request.data["is_default"] = True
            serializer = CreateUpdateAddressInfoSerializer(
                address, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                defaulted_address = serializer.save()
                create_log("INFO", "Defaulted Address", defaulted_address)
                if defaulted_address:
                    return Response(
                        data={"detail": "Address defaulted"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    data={"detail": "Unable to set default Address"},
                    status=status.HTTP_409_CONFLICT,
                )
            else:
                create_log("ERROR", "Error Address Default", serializer.errors)
                return Response(
                    data={"detail": "Unable to set default Address"},
                    status=status.HTTP_409_CONFLICT,
                )
        return Response(
            data={"detail": "Unable to set default Address"},
            status=status.HTTP_409_CONFLICT,
        )


class DeleteAddressMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        address = AddressInfo.objects.get(id=request.data.get("id"))
        request.data["is_deleted"] = True
        serializer = CreateUpdateAddressInfoSerializer(
            address, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            deleted_address = serializer.save()
            create_log("INFO", "Deleted Address", deleted_address)
            if deleted_address:
                return Response(
                    data={"detail": "Address deleted"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                data={"detail": "Unable to delete Address"},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            create_log("ERROR", "Error Address Delete", serializer.errors)
            return Response(
                data={"detail": "Unable to delete Address"},
                status=status.HTTP_409_CONFLICT,
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


# Shop
class VerifyCodeView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        is_verified, message, code = verify_code_details(request)

        if not is_verified:
            return Response(
                data={"details": message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data={"details": message, "code": {"code_id": code.id, "code": code.code, "code_status": code.status}},
            status=status.HTTP_200_OK,
        )

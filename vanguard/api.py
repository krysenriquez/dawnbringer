from django.core.validators import validate_email
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.enums import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from accounts.models import Account
from users.models import User
from vanguard.serializers import AuthAdminLoginSerializer, AuthLoginSerializer, AuthRefreshSerializer
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser, IsMemberUser
from request_logging.decorators import no_logging
from vanguard.services import notify_customer_on_forgot_password_by_email, verify_forgot_password_link


class AuthAdminLoginView(TokenObtainPairView):
    serializer_class = AuthAdminLoginSerializer

    @no_logging()
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AuthLoginView(TokenObtainPairView):
    serializer_class = AuthLoginSerializer

    @no_logging()
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AuthShopLoginView(TokenObtainPairView):
    serializer_class = AuthLoginSerializer

    @no_logging()
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AuthRefreshView(TokenRefreshView):
    serializer_class = AuthRefreshSerializer


class WhoAmIAdminView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        data = {
            "user_id": request.user.user_id,
            "display_name": request.user.display_name,
            "email_address": request.user.email_address,
            "username": request.user.username,
            "user_type": request.user.user_type.user_type_name,
        }

        if request.user.avatar and hasattr(request.user.avatar, "url"):
            data["user_avatar"] = request.build_absolute_uri(request.user.avatar.url)

        return Response(
            data=data,
            status=status.HTTP_200_OK,
        )


class WhoAmIMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        data = {
            "user_id": request.user.user_id,
            "display_name": request.user.display_name,
            "email_address": request.user.email_address,
            "username": request.user.username,
            "user_type": request.user.user_type.user_type_name,
        }

        account = Account.objects.get(user=request.user)
        if account.avatar_info.avatar and hasattr(account.avatar_info.avatar, "url"):
            data["user_avatar"] = request.build_absolute_uri(account.avatar_info.avatar.url)

        return Response(
            data=data,
            status=status.HTTP_200_OK,
        )


class WhoAmIShopView(views.APIView):
    def post(self, request, *args, **kwargs):
        if request.user.user_type.user_type_name == UserType.MEMBER:
            data = {
                "user_id": request.user.user_id,
                "email_address": request.user.email_address,
                "username": request.user.username,
                "user_type": request.user.user_type.user_type_name,
            }

            account = Account.objects.get(user=request.user)
            if account.avatar_info.avatar and hasattr(account.avatar_info.avatar, "url"):
                data["user_avatar"] = request.build_absolute_uri(account.avatar_info.avatar.url)

            data["address_info"] = account.address_info.values()
            data["account_id"] = account.account_id
            data["first_name"] = account.first_name
            data["last_name"] = account.last_name
            data["contact_number"] = account.contact_info.contact_number

            return Response(
                data=data,
                status=status.HTTP_200_OK,
            )

        return Response(
            data="Invalid Member Account",
            status=status.HTTP_200_OK,
        )


class LogoutView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.data.get("all"):
            token: OutstandingToken
            for token in OutstandingToken.objects.filter(user=request.user):
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response({"status": "OK, goodbye, all refresh tokens blacklisted"})
        refresh_token = self.request.data.get("refresh_token")
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response({"status": "OK, goodbye"})


class ForgotPasswordAdminView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email_address = request.data.get("recovery_email")
        try:
            validate_email(email_address)
            try:
                user = User.objects.get(email_address=email_address)
            except User.DoesNotExist:
                return Response(
                    data={"message": "Invalid Recovery Email Address"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                email_msg = notify_customer_on_forgot_password_by_email(user,False)
                return Response(
                    data={"message": email_msg},
                    status=status.HTTP_200_OK,
                )
        except ValidationError:
            return Response(
                data={"message": "Please enter a valid Email Address format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class ForgotPasswordMemberView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email_address = request.data.get("recovery_email")
        try:
            validate_email(email_address)
            try:
                user = User.objects.get(email_address=email_address)
            except User.DoesNotExist:
                return Response(
                    data={"message": "Invalid Recovery Email Address"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                email_msg = notify_customer_on_forgot_password_by_email(user, True)
                return Response(
                    data={"message": email_msg},
                    status=status.HTTP_200_OK,
                )
        except ValidationError:
            return Response(
                data={"message": "Please enter a valid Email Address format."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyForgotPasswordView(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data.get("data")
        is_verified, unsigned_obj = verify_forgot_password_link(data)
        if is_verified:
            user = User.objects.get(id=unsigned_obj["user"])
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"message": unsigned_obj},
            status=status.HTTP_400_BAD_REQUEST,
        )

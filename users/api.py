from difflib import SequenceMatcher
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from logs.services import create_log
from users.serializers import (
    ModulesSerializer,
    PermissionsSerializer,
    UserPermissionsSerializer,
    UserTypeInfoSerializer,
    UserTypesListSerializer,
    UserTypesOptionsSerializer,
    UsersListSerializer,
    UserInfoSerializer,
    CreateUpdateUserSerializer,
    ContentTypeSerializer,
    UserLogsSerializer,
)
from users.models import User, UserLogs, LogDetails, UserType, Module, Permission
from users.services import (
    create_branch_assignment,
    process_create_user_request,
    transform_user_form_data_to_json,
    update_branch_assignments,
    update_role_permissions,
)
from vanguard.permissions import IsDeveloperUser, IsAdminUser, IsStaffUser, IsMemberUser
from vanguard.throttle import ThirtyPerMinuteAnonThrottle


class ContentTypeViewSet(ModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = ContentType.objects.all()
        model = self.request.query_params.get("model", None)

        if model is not None:
            queryset = queryset.filter(model=model)

        return queryset


class UserTypesOptionsViewSet(ModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypesOptionsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return UserType.objects.all()


class UserTypesListViewSet(ModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypesListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return UserType.objects.all()


class UserTypeInfoViewSet(ModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypeInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        user_type_id = self.request.query_params.get("user_type_id", None)
        return UserType.objects.filter(user_type_id=user_type_id)


class ModulesViewSet(ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModulesSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Module.objects.all()


class PermissionsListViewSet(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return Permission.objects.all()


class UsersListViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersListSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return User.objects.exclude(is_active=False).order_by("-id")


class UserInfoViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id", None)
        return User.objects.exclude(is_active=False).filter(user_id=user_id)


class UserProfileViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return User.objects.exclude(is_active=False).filter(id=self.request.user.pk)


class UserLogsViewSet(ModelViewSet):
    queryset = UserLogs.objects.all()
    serializer_class = UserLogsSerializer
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = UserLogs.objects.order_by("-id")
        content_type = self.request.query_params.get("content_type", None)
        object_id = self.request.query_params.get("object_id", None)
        user = self.request.query_params.get("user", None)

        if content_type is not None:
            queryset = queryset.filter(content_type=content_type, object_id=object_id)

        if user is not None:
            queryset = queryset.filter(user=user)

        return queryset


class CreateUserView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser]

    def post(self, request, *args, **kwargs):
        processed_request = process_create_user_request(request)
        serializer = CreateUpdateUserSerializer(data=processed_request)
        if serializer.is_valid():
            user = serializer.save()
            assignment = create_branch_assignment(user)
            if assignment:
                return Response(data={"detail": "User created."}, status=status.HTTP_201_CREATED)
            return Response(
                data={"detail": "User created. Unable to create Branch Assignments."}, status=status.HTTP_201_CREATED
            )
        else:
            print(serializer.errors)
            return Response(
                data={"detail": "Unable to create User."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateBranchAssignmentsView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser]

    def post(self, request, *args, **kwargs):
        try:
            update_branch_assignments(request)
            return Response(
                data={"detail": "Branch User Assignments updated"},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                data={"detail": "Unable to update Branch User Assignments"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateRolePermissionsView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser]

    def post(self, request, *args, **kwargs):
        try:
            update_role_permissions(request)
            return Response(
                data={"detail": "Role Permissions updated"},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                data={"detail": "Unable to update Role Permissions"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateUserProfileMemberView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        data = transform_user_form_data_to_json(request.data)
        serializer = CreateUpdateUserSerializer(
            self.request.user, data=data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            updated_user = serializer.save()
            create_log("INFO", "Updated User (Admin)", updated_user)
            if updated_user:
                return Response(
                    data={"detail": "Account updated"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                data={"detail": "Unable to update Account"},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            create_log("ERROR", "Error User Update (Admin)", serializer.errors)
            return Response(
                data={"detail": "Unable to update Account"},
                status=status.HTTP_409_CONFLICT,
            )


# Admin
class CheckUsernameAdminView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(data={"detail": "Username available."}, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"detail": "Sorry, Username unavailable."},
                status=status.HTTP_409_CONFLICT,
            )


class ChangeUsernameAdminView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        new_username = request.data.get("username")
        password = request.data.get("confirm_password")
        logged_user = self.request.user
        try:
            user = User.objects.get(username=new_username)
        except User.DoesNotExist:
            if not logged_user.check_password(password):
                return Response(
                    data={"detail": "Invalid Current Password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = {"username": new_username, "can_change_username": False}
            serializer = CreateUpdateUserSerializer(logged_user, data=data, partial=True, context={"request": request})
            if serializer.is_valid():
                print(serializer)
                serializer.save()
                return Response(data={"detail": "Username has been updated"}, status=status.HTTP_200_OK)
            return Response(data={"detail": "Unable to update username"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if user != logged_user:
                return Response(
                    data={"detail": "Username unavailable."},
                    status=status.HTTP_409_CONFLICT,
                )
            else:
                return Response(
                    data={"detail": "Retaining Username."},
                    status=status.HTTP_200_OK,
                )


class CheckEmailAddressAdminView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        email_address = request.data.get("email_address")
        try:
            validate_email(email_address)
            try:
                user = User.objects.get(email_address=email_address)
            except User.DoesNotExist:
                return Response(
                    data={"detail": "Email Address available"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data={"detail": "Sorry, Email Address unavailable."},
                    status=status.HTTP_409_CONFLICT,
                )
        except ValidationError:
            return Response(
                data={"detail": "Please enter a valid Email Address format."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangeEmailAddressAdminView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        email_address = request.data.get("email_address")
        password = request.data.get("confirm_password")
        logged_user = self.request.user
        try:
            validate_email(email_address)
            try:
                user = User.objects.get(email_address=email_address)
            except User.DoesNotExist:
                if not logged_user.check_password(password):
                    return Response(
                        data={"detail": "Invalid Current Password."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                data = {"email_address": email_address, "can_change_email_address": False}
                serializer = CreateUpdateUserSerializer(
                    logged_user, data=data, partial=True, context={"request": request}
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        data={"detail": "Email Address has been updated"},
                        status=status.HTTP_200_OK,
                    )
                return Response(data={"detail": "Unable to update Email Address"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if user != logged_user:
                    return Response(
                        data={"detail": "Email Address unavailable."},
                        status=status.HTTP_409_CONFLICT,
                    )
                else:
                    return Response(
                        data={"detail": "Retaining Email Address."},
                        status=status.HTTP_200_OK,
                    )
        except ValidationError:
            return Response(
                data={"detail": "Please enter a valid Email Address format."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordAdminView(views.APIView):
    model = User
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        new_password = request.data.get("new_password")
        password = request.data.get("current_password")
        logged_user = self.request.user

        if not logged_user.check_password(password):
            return Response(
                data={"detail": "Invalid Current Password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logged_user.set_password(new_password)
        logged_user.can_change_password = False
        logged_user.save()

        return Response(data={"detail": "Password Updated."}, status=status.HTTP_200_OK)


class ResetPasswordAdminView(views.APIView):
    model = User
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        new_password = request.data.get("new_password")
        refresh_token = self.request.data.get("refresh")
        logged_user = self.request.user
        logged_user.set_password(new_password)
        logged_user.save()
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response(data={"detail": "Password Updated."}, status=status.HTTP_200_OK)


class ChangeMemberUsernameAdminView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        new_username = request.data.get("username")
        password = request.data.get("admin_password")
        member_user = User.objects.get(user_id=request.data.get("user_id"))
        logged_user = self.request.user

        try:
            user = User.objects.get(username=new_username)
        except User.DoesNotExist:
            if not logged_user.check_password(password):
                return Response(
                    data={"detail": "Invalid Admin Password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = {"username": new_username, "can_change_username": False}
            serializer = CreateUpdateUserSerializer(member_user, data=data, partial=True, context={"request": request})

            if serializer.is_valid():
                serializer.save()
                return Response(data={"detail": "Username has been updated"}, status=status.HTTP_200_OK)
            return Response(data={"detail": "Unable to update username"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if user != member_user:
                return Response(
                    data={"detail": "Username unavailable."},
                    status=status.HTTP_409_CONFLICT,
                )
            else:
                return Response(
                    data={"detail": "Retaining Username."},
                    status=status.HTTP_200_OK,
                )


class ChangeMemberEmailAddressAdminView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        email_address = request.data.get("email_address")
        password = request.data.get("admin_password")
        member_user = User.objects.get(user_id=request.data.get("user_id"))
        logged_user = self.request.user

        try:
            validate_email(email_address)
            try:
                user = User.objects.get(email_address=email_address)
            except User.DoesNotExist:
                if not logged_user.check_password(password):
                    return Response(
                        data={"detail": "Invalid Admin Password."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                data = {"email_address": email_address, "can_change_email_address": False}
                serializer = CreateUpdateUserSerializer(
                    member_user, data=data, partial=True, context={"request": request}
                )

                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        data={"detail": "Email Address has been updated"},
                        status=status.HTTP_200_OK,
                    )
                return Response(data={"detail": "Unable to update Email Address"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if user != member_user:
                    return Response(
                        data={"detail": "Email Address unavailable."},
                        status=status.HTTP_409_CONFLICT,
                    )
                else:
                    return Response(
                        data={"detail": "Retaining Email Address."},
                        status=status.HTTP_200_OK,
                    )
        except ValidationError:
            return Response(
                data={"detail": "Please enter a valid Email Address format."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangeMemberPasswordAdminView(views.APIView):
    model = User
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        new_password = request.data.get("new_password")
        password = request.data.get("admin_password")
        member_user = User.objects.get(user_id=request.data.get("user_id"))
        logged_user = self.request.user

        if not logged_user.check_password(password):
            return Response(
                data={"detail": "Invalid Admin Password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        member_user.set_password(new_password)
        member_user.can_change_password = False
        member_user.save()

        return Response(data={"detail": "Password Updated."}, status=status.HTTP_200_OK)

class RetrieveRolePermissionsView(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser]

    def post(self, request, *args, **kwargs):
        role_permission = Permission.objects.filter(user_type=request.user.user_type)
        serializer = UserPermissionsSerializer(role_permission, many=True)
        print(serializer.data)
        return Response(
            data={"permissions": serializer.data},
            status=status.HTTP_200_OK,
        )
# Member
class ChangeUsernameMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        new_username = request.data.get("username")
        password = request.data.get("confirm_password")
        logged_user = self.request.user
        try:
            user = User.objects.get(username=new_username)
        except User.DoesNotExist:
            if not logged_user.check_password(password):
                return Response(
                    data={"detail": "Invalid Current Password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = {"username": new_username, "can_change_username": False}
            serializer = CreateUpdateUserSerializer(logged_user, data=data, partial=True, context={"request": request})
            if serializer.is_valid():
                print(serializer)
                serializer.save()
                return Response(data={"detail": "Username has been updated"}, status=status.HTTP_200_OK)
            return Response(data={"detail": "Unable to update username"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if user != logged_user:
                return Response(
                    data={"detail": "Username unavailable."},
                    status=status.HTTP_409_CONFLICT,
                )
            else:
                return Response(
                    data={"detail": "Retaining Username."},
                    status=status.HTTP_200_OK,
                )


class ChangeEmailAddressMemberView(views.APIView):
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        email_address = request.data.get("email_address")
        password = request.data.get("confirm_password")
        logged_user = self.request.user
        try:
            validate_email(email_address)
            try:
                user = User.objects.get(email_address=email_address)
            except User.DoesNotExist:
                if not logged_user.check_password(password):
                    return Response(
                        data={"detail": "Invalid Current Password."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                data = {"email_address": email_address, "can_change_email_address": False}
                serializer = CreateUpdateUserSerializer(
                    logged_user, data=data, partial=True, context={"request": request}
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        data={"detail": "Email Address has been updated"},
                        status=status.HTTP_200_OK,
                    )
                return Response(data={"detail": "Unable to update Email Address"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if user != logged_user:
                    return Response(
                        data={"detail": "Email Address unavailable."},
                        status=status.HTTP_409_CONFLICT,
                    )
                else:
                    return Response(
                        data={"detail": "Retaining Email Address."},
                        status=status.HTTP_200_OK,
                    )
        except ValidationError:
            return Response(
                data={"detail": "Please enter a valid Email Address format."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordMemberView(views.APIView):
    model = User
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        new_password = request.data.get("new_password")
        password = request.data.get("current_password")
        logged_user = self.request.user

        if not logged_user.check_password(password):
            return Response(
                data={"detail": "Invalid Current Password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logged_user.set_password(new_password)
        logged_user.can_change_password = False
        logged_user.save()

        return Response(data={"detail": "Password Updated."}, status=status.HTTP_200_OK)


class ResetPasswordMemberView(views.APIView):
    model = User
    permission_classes = [IsMemberUser]

    def post(self, request, *args, **kwargs):
        new_password = request.data.get("new_password")
        refresh_token = self.request.data.get("refresh")
        logged_user = self.request.user
        logged_user.set_password(new_password)
        logged_user.save()
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response(data={"detail": "Password Updated."}, status=status.HTTP_200_OK)


class PasswordValidation(views.APIView):
    permission_classes = [IsDeveloperUser | IsAdminUser | IsStaffUser | IsMemberUser]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        emailAddress = request.data.get("email_address")
        password = request.data.get("password")
        max_similarity = 0.7
        if SequenceMatcher(password.lower(), username.lower()).quick_ratio() > max_similarity:
            return Response(
                data={"detail": "The password is too similar to the username.", "similar": True},
                status=status.HTTP_403_FORBIDDEN,
            )
        if SequenceMatcher(password.lower(), emailAddress.lower()).quick_ratio() > max_similarity:
            return Response(
                data={"detail": "The password is too similar to the email.", "similar": True},
                status=status.HTTP_403_FORBIDDEN,
            )


# Anon
class CheckUsernameAnonView(views.APIView):
    permission_classes = []
    throttle_classes = [ThirtyPerMinuteAnonThrottle]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(data={"detail": "Username available."}, status=status.HTTP_200_OK)
        else:

            return Response(
                data={"detail": "Sorry, Username unavailable."},
                status=status.HTTP_409_CONFLICT,
            )


class CheckEmailAddressAnonView(views.APIView):
    permission_classes = []
    throttle_classes = [ThirtyPerMinuteAnonThrottle]

    def post(self, request, *args, **kwargs):
        email_address = request.data.get("email_address")
        try:
            validate_email(email_address)
            try:
                user = User.objects.get(email_address=email_address)
            except User.DoesNotExist:
                return Response(
                    data={"detail": "Email Address available"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data={"detail": "Sorry, Email Address unavailable."},
                    status=status.HTTP_409_CONFLICT,
                )
        except ValidationError:
            return Response(
                data={"detail": "Please enter a valid Email Address format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

from rest_framework.routers import DefaultRouter
from django.urls import path
from users.api import (
    ContentTypeViewSet,
    UserTypesOptionsViewSet,
    UserTypesListViewSet,
    UserTypeInfoViewSet,
    ModulesViewSet,
    PermissionsListViewSet,
    UsersListViewSet,
    UserInfoViewSet,
    UserLogsViewSet,
    CreateUserView,
    UpdateBranchAssignmentsView,
    UpdateRolePermissionsView,
    CheckUsernameView,
    ChangeUsernameAdminView,
    ChangeEmailAddressAdminView,
    ChangePasswordAdminView,
    ChangeUsernameView,
    CheckEmailAddressView,
    ChangeEmailAddressView,
    ChangePasswordView,
    ResetPasswordView,
    PasswordValidation,
)

router = DefaultRouter()
router.register(r"getusertypesoptions", UserTypesOptionsViewSet)
router.register(r"getusertypes", UserTypesListViewSet)
router.register(r"getusertype", UserTypeInfoViewSet)
router.register(r"getmodules", ModulesViewSet)
router.register(r"getpermissions", PermissionsListViewSet)
router.register(r"getusers", UsersListViewSet)
router.register(r"getuser", UserInfoViewSet)
router.register(r"userlogs", UserLogsViewSet)
router.register(r"contenttype", ContentTypeViewSet)

urlpatterns = [
    path("updatebranchassignments/", UpdateBranchAssignmentsView.as_view()),
    path("updaterolepermissions/", UpdateRolePermissionsView.as_view()),
    path("checkusername/", CheckUsernameView.as_view()),
    path("checkemailaddress/", CheckEmailAddressView.as_view()),
    path("resetpassword/", ResetPasswordView.as_view()),
    path("checkpassword/", PasswordValidation.as_view()),
    # Admin
    path("createuser/", CreateUserView.as_view()),
    path("changeusernameadmin/", ChangeUsernameAdminView.as_view()),
    path("changeemailaddressadmin/", ChangeEmailAddressAdminView.as_view()),
    path("changepasswordadmin/", ChangePasswordAdminView.as_view()),
    # Member
    path("changeusername/", ChangeUsernameView.as_view()),
    path("changeemailaddress/", ChangeEmailAddressView.as_view()),
    path("changepassword/", ChangePasswordView.as_view()),
]

urlpatterns += router.urls

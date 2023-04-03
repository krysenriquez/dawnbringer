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
    UserProfileViewSet,
    UserLogsViewSet,
    CreateUserView,
    UpdateBranchAssignmentsView,
    UpdateRolePermissionsView,
    # Admin
    CheckUsernameAdminView,
    ChangeUsernameAdminView,
    CheckEmailAddressAdminView,
    ChangeEmailAddressAdminView,
    ChangePasswordAdminView,
    ChangePasswordMemberView,
    ResetPasswordAdminView,
    ChangeMemberUsernameAdminView,
    ChangeMemberEmailAddressAdminView,
    ChangeMemberPasswordAdminView,
    RetrieveRolePermissionsView,
    # Member
    CheckUsernameAnonView,
    ChangeUsernameMemberView,
    CheckEmailAddressAnonView,
    ChangeEmailAddressMemberView,
    ResetPasswordMemberView,
    UpdateUserProfileMemberView,
)

router = DefaultRouter()
router.register(r"admin/getusertypesoptions", UserTypesOptionsViewSet)
router.register(r"admin/getusertypes", UserTypesListViewSet)
router.register(r"admin/getusertype", UserTypeInfoViewSet)
router.register(r"admin/getmodules", ModulesViewSet)
router.register(r"admin/getpermissions", PermissionsListViewSet)
router.register(r"admin/getusers", UsersListViewSet)
router.register(r"admin/getuser", UserInfoViewSet)
router.register(r"admin/getuserprofile", UserProfileViewSet)
router.register(r"admin/userlogs", UserLogsViewSet)
router.register(r"admin/contenttype", ContentTypeViewSet)

urlpatterns = [
    # Admin
    path("admin/updatebranchassignments/", UpdateBranchAssignmentsView.as_view()),
    path("admin/updaterolepermissions/", UpdateRolePermissionsView.as_view()),
    path("admin/updateuserprofile/", UpdateUserProfileMemberView.as_view()),
    path("admin/createuser/", CreateUserView.as_view()),
    path("admin/checkusername/", CheckUsernameAdminView.as_view()),
    path("admin/changeusername/", ChangeUsernameAdminView.as_view()),
    path("admin/checkemailaddress/", CheckEmailAddressAdminView.as_view()),
    path("admin/changeemailaddress/", ChangeEmailAddressAdminView.as_view()),
    path("admin/changepassword/", ChangePasswordAdminView.as_view()),
    path("admin/resetpassword/", ResetPasswordAdminView.as_view()),
    path("admin/changememberusername/", ChangeMemberUsernameAdminView.as_view()),
    path("admin/changememberemailaddress/", ChangeMemberEmailAddressAdminView.as_view()),
    path("admin/changememberpassword/", ChangeMemberPasswordAdminView.as_view()),
    path("admin/getuserpermissions/", RetrieveRolePermissionsView.as_view()),
    # Member
    path("member/changeusername/", ChangeUsernameMemberView.as_view()),
    path("member/changeemailaddress/", ChangeEmailAddressMemberView.as_view()),
    path("member/changepassword/", ChangePasswordMemberView.as_view()),
    path("member/resetpassword/", ResetPasswordMemberView.as_view()),
    # Anon
    path("member/checkusername/", CheckUsernameAnonView.as_view()),
    path("member/checkemailaddress/", CheckEmailAddressAnonView.as_view()),
]

urlpatterns += router.urls

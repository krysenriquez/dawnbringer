from rest_framework.routers import DefaultRouter
from django.urls import path
from users.api import (
    UsersListViewSet,
    UserInfoViewSet,
    UserLogsViewSet,
    ContentTypeViewSet,
    UpdateBranchAssignmentsView,
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
router.register(r"getusers", UsersListViewSet)
router.register(r"getuser", UserInfoViewSet)
router.register(r"userlogs", UserLogsViewSet)
router.register(r"contenttype", ContentTypeViewSet)

urlpatterns = [
    path("updatebranchassignments/", UpdateBranchAssignmentsView.as_view()),
    path("checkusername/", CheckUsernameView.as_view()),
    path("checkemailaddress/", CheckEmailAddressView.as_view()),
    path("resetpassword/", ResetPasswordView.as_view()),
    path("checkpassword/", PasswordValidation.as_view()),
    # Admin
    path("changeusernameadmin/", ChangeUsernameAdminView.as_view()),
    path("changeemailaddressadmin/", ChangeEmailAddressAdminView.as_view()),
    path("changepasswordadmin/", ChangePasswordAdminView.as_view()),
    # Member
    path("changeusername/", ChangeUsernameView.as_view()),
    path("changeemailaddress/", ChangeEmailAddressView.as_view()),
    path("changepassword/", ChangePasswordView.as_view()),
]

urlpatterns += router.urls

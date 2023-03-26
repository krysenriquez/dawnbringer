from rest_framework.routers import DefaultRouter
from accounts.api import (
    AddressMemberInfoViewSet,
    AccountAdminListViewSet,
    AccountAdminInfoViewSet,
    AccountUserInfoAdminViewSet,
    AccountCashoutMethodsMemberViewSet,
    AccountMemberInfoViewSet,
    AccountProfileInfoViewSet,
    RegisterAccountView,
    VerifyRegistrationView,
    VerifyAccountView,
    UpdateAccountAdminView,
    UpdateAccountMemberView,
    CreateAddressMemberView,
    UpdateAddressMemberView,
    UpdateDefaultAddressMemberView,
    DeleteAddressMemberView,
)
from django.urls import path

router = DefaultRouter()
# Admin
router.register(r"getmembers", AccountAdminListViewSet)
router.register(r"getmember", AccountAdminInfoViewSet)
router.register(r"getmemberuser", AccountUserInfoAdminViewSet)
# Member
router.register(r"getaccount", AccountMemberInfoViewSet)
router.register(r"getprofile", AccountProfileInfoViewSet)
router.register(r"getaddress", AddressMemberInfoViewSet)
router.register(r"getaccountcashoutmethods", AccountCashoutMethodsMemberViewSet)
urlpatterns = [
    path("verifyaccount/", VerifyAccountView.as_view()),
    # Admin
    path("updateadminprofile/", UpdateAccountAdminView.as_view()),
    # Members
    path("register/", RegisterAccountView.as_view()),
    path("verifyregistration/", VerifyRegistrationView.as_view()),
    path("updateprofile/", UpdateAccountMemberView.as_view()),
    path("createaddress/", CreateAddressMemberView.as_view()),
    path("updateaddress/", UpdateAddressMemberView.as_view()),
    path("updatedefaultaddress/", UpdateDefaultAddressMemberView.as_view()),
    path("deleteaddress/", DeleteAddressMemberView.as_view()),
]

urlpatterns += router.urls

from rest_framework.routers import DefaultRouter
from accounts.api import (
    AddressMemberInfoViewSet,
    AccountAdminListViewSet,
    AccountAdminInfoViewSet,
    AccountUserInfoAdminViewSet,
    AccountCashoutMethodsMemberViewSet,
    AccountMemberInfoViewSet,
    AccountProfileInfoViewSet,
    UpdateCodeStatusView,
    RegisterAccountView,
    VerifyRegistrationView,
    UpdateAccountMemberView,
    CreateAddressMemberView,
    UpdateAddressMemberView,
    UpdateDefaultAddressMemberView,
    DeleteAddressMemberView,
)
from django.urls import path

router = DefaultRouter()
# Admin
router.register(r"admin/getmembers", AccountAdminListViewSet)
router.register(r"admin/getmember", AccountAdminInfoViewSet)
router.register(r"admin/getmemberuser", AccountUserInfoAdminViewSet)
# Member
router.register(r"member/getaccount", AccountMemberInfoViewSet)
router.register(r"member/getprofile", AccountProfileInfoViewSet)
router.register(r"member/getaddress", AddressMemberInfoViewSet)
router.register(r"member/getaccountcashoutmethods", AccountCashoutMethodsMemberViewSet)
urlpatterns = [
    path("admin/updatecodestatus/", UpdateCodeStatusView.as_view()),
    # Members
    path("member/register/", RegisterAccountView.as_view()),
    path("member/verifyregistration/", VerifyRegistrationView.as_view()),
    path("member/updateprofile/", UpdateAccountMemberView.as_view()),
    path("member/createaddress/", CreateAddressMemberView.as_view()),
    path("member/updateaddress/", UpdateAddressMemberView.as_view()),
    path("member/updatedefaultaddress/", UpdateDefaultAddressMemberView.as_view()),
    path("member/deleteaddress/", DeleteAddressMemberView.as_view()),
]

urlpatterns += router.urls

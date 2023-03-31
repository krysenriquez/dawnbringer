from rest_framework.routers import DefaultRouter
from django.urls import path
from core.api import (
    SettingsListViewSet,
    SettingInfoViewSet,
    MembershipLevelsAdminViewSet,
    MembershipLevelsMemberViewSet,
    ActivitiesListMemberViewSet,
    CashoutAdminListViewSet,
    CashoutAdminInfoViewSet,
    CashoutMemberInfoViewSet,
    CashoutMemberListViewSet,
    GetMembershipLevelPointsAdminView,
    GetMembershipLevelPointsMemberView,
    GetPointConversionRateView,
    GetMaxPointConversionAmountView,
    CreateConversionView,
    UpdateSettingsView,
    UpdateMembershipLevelsView,
    CashoutMethodsListViewSet,
    GetWalletCanCashoutView,
    GetWalletScheduleView,
    GetMaxWalletAmountView,
    GetWalletTotalCashoutView,
    GetWalletTotalFeeView,
    RequestCashoutView,
    UpdateCashoutStatusView,
)

router = DefaultRouter()
# Admin
router.register(r"admin/getsettings", SettingsListViewSet)
router.register(r"admin/getsetting", SettingInfoViewSet)
router.register(r"admin/getmembershiplevels", MembershipLevelsAdminViewSet)
router.register(r"admin/getcashouts", CashoutAdminListViewSet)
router.register(r"admin/getcashoutinfo", CashoutAdminInfoViewSet)
# Member
router.register(r"member/getmembershiplevels", MembershipLevelsMemberViewSet)
router.register(r"member/getactivities", ActivitiesListMemberViewSet)
router.register(r"member/getcashouts", CashoutMemberListViewSet)
router.register(r"member/getcashoutinfo", CashoutMemberInfoViewSet)
router.register(r"member/getdefaultcashoutmethods", CashoutMethodsListViewSet)

urlpatterns = [
    # Admin
    path("admin/updatesettings/", UpdateSettingsView.as_view()),
    path("admin/updatemembershiplevels/", UpdateMembershipLevelsView.as_view()),
    path("admin/updatecashoutstatus/", UpdateCashoutStatusView.as_view()),
    path("admin/getmembershiplevelpoints/", GetMembershipLevelPointsAdminView.as_view()),
    # Member
    path("member/getmembershiplevelpoints/", GetMembershipLevelPointsMemberView.as_view()),
    path("member/getconversionrate/", GetPointConversionRateView.as_view()),
    path("member/checkmaxconversionamount/", GetMaxPointConversionAmountView.as_view()),
    path("member/convertpoints/", CreateConversionView.as_view()),
    path("member/getwalletcancashout/", GetWalletCanCashoutView.as_view()),
    path("member/getwalletcashoutschedules/", GetWalletScheduleView.as_view()),
    path("member/getwalletmaxcashout/", GetMaxWalletAmountView.as_view()),
    path("member/getwallettotalcashout/", GetWalletTotalCashoutView.as_view()),
    path("member/getwallettotalfee/", GetWalletTotalFeeView.as_view()),
    path("member/requestcashout/", RequestCashoutView.as_view()),
]


urlpatterns += router.urls

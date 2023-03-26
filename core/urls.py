from rest_framework.routers import DefaultRouter
from django.urls import path
from core.api import (
    SettingsListViewSet,
    SettingInfoViewSet,
    MembershipLevelsViewSet,
    ActivitiesListMemberViewSet,
    CashoutAdminListViewSet,
    CashoutAdminInfoViewSet,
    CashoutMemberInfoViewSet,
    CashoutMemberListViewSet,
    GetMembershipLevelPointsView,
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
router.register(r"getsettings", SettingsListViewSet)
router.register(r"getsetting", SettingInfoViewSet)
router.register(r"getmembershiplevels", MembershipLevelsViewSet)
router.register(r"getadmincashouts", CashoutAdminListViewSet)
router.register(r"getadmincashoutinfo", CashoutAdminInfoViewSet)
# Member
router.register(r"getmemberactivities", ActivitiesListMemberViewSet)
router.register(r"getcashouts", CashoutMemberListViewSet)
router.register(r"getcashoutinfo", CashoutMemberInfoViewSet)
router.register(r"getdefaultcashoutmethods", CashoutMethodsListViewSet)

urlpatterns = [
    # Admin
    path("updatesettings/", UpdateSettingsView.as_view()),
    path("updatemembershiplevels/", UpdateMembershipLevelsView.as_view()),
    path("updatecashoutstatus/", UpdateCashoutStatusView.as_view()),
    # Member
    path("getmembershiplevelpoints/", GetMembershipLevelPointsView.as_view()),
    path("getconversionrate/", GetPointConversionRateView.as_view()),
    path("checkmaxconversionamount/", GetMaxPointConversionAmountView.as_view()),
    path("convertpoints/", CreateConversionView.as_view()),
    # Member Cashouts
    path("getwalletcancashout/", GetWalletCanCashoutView.as_view()),
    path("getwalletcashoutschedules/", GetWalletScheduleView.as_view()),
    path("getwalletmaxcashout/", GetMaxWalletAmountView.as_view()),
    path("getwallettotalcashout/", GetWalletTotalCashoutView.as_view()),
    path("getwallettotalfee/", GetWalletTotalFeeView.as_view()),
    path("requestcashout/", RequestCashoutView.as_view()),
]


urlpatterns += router.urls

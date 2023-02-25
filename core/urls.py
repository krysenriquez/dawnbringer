from rest_framework.routers import DefaultRouter
from django.urls import path
from core.api import (
    SettingsViewSet,
    MembershipLevelsViewSet,
    ActivitiesListMemberViewSet,
    UpdateSettingsView,
    UpdateMembershipLevelsView,
    Test,
)

router = DefaultRouter()
# Admin
router.register(r"getsettings", SettingsViewSet)
router.register(r"getmembershiplevels", MembershipLevelsViewSet)
# Member
router.register(r"getmemberactivities", ActivitiesListMemberViewSet)
urlpatterns = [
    path("updatesettings/", UpdateSettingsView.as_view()),
    path("updatemembershiplevels/", UpdateMembershipLevelsView.as_view()),
    path("test/", Test.as_view()),
]


urlpatterns += router.urls

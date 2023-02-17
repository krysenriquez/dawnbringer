from rest_framework.routers import DefaultRouter
from django.urls import path
from core.api import (
    SettingsViewSet,
    MembershipLevelsViewSet,
    UpdateSettingsView,
    UpdateMembershipLevelsView,
    Test,
)

router = DefaultRouter()
# Admin
router.register(r"getsettings", SettingsViewSet)
router.register(r"getmembershiplevels", MembershipLevelsViewSet)

urlpatterns = [
    path("updatesettings/", UpdateSettingsView.as_view()),
    path("updatemembershiplevels/", UpdateMembershipLevelsView.as_view()),
    path("test/", Test.as_view()),
]


urlpatterns += router.urls

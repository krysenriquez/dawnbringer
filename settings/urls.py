from rest_framework.routers import DefaultRouter
from django.urls import path
from settings.api import (
    SettingsViewSet,
    MembershipLevelsViewSet,
    UpdateSettingsView,
    UpdateMembershipLevelsView,
)

router = DefaultRouter()
router.register(r"getadminsettings", SettingsViewSet)
router.register(r"getmembershiplevels", MembershipLevelsViewSet)

urlpatterns = [
    path("updateadminsettings/", UpdateSettingsView.as_view()),
    path("updatemembershiplevels/", UpdateMembershipLevelsView.as_view()),
]

urlpatterns += router.urls

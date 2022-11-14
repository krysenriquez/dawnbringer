from django.urls import path
from vanguard.api import (
    AdminLoginView,
    LogoutView,
    MemberLoginView,
    WhichUserView,
    WhoAmIMemberView,
    WhoAmIAdminView,
)

urlpatterns = [
    path("admin/", AdminLoginView.as_view()),
    path("member/", MemberLoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("whoamimember/", WhoAmIMemberView.as_view()),
    path("whoamiadmin/", WhoAmIAdminView.as_view()),
    path("whichuser/", WhichUserView.as_view()),
]

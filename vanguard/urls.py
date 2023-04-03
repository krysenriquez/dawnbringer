from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from vanguard.api import (
    AuthRefreshView,
    WhoAmIAdminView,
    WhoAmIMemberView,
    AuthAdminLoginView,
    AuthLoginView,
    LogoutView,
    ForgotPasswordAdminView,
    ForgotPasswordMemberView,
    VerifyForgotPasswordView,
)

urlpatterns = [
    # Admin
    path("admin/login/", AuthAdminLoginView.as_view()),
    path("admin/whoami/", WhoAmIAdminView.as_view()),
    path("admin/logout/", LogoutView.as_view()),
    path("admin/refresh/", AuthRefreshView.as_view()),
    path("admin/forgotpassword/", ForgotPasswordAdminView.as_view()),
    path("admin/verifyforgotpassword/", VerifyForgotPasswordView.as_view()),
    # Member
    path("member/login/", AuthLoginView.as_view()),
    path("member/whoami/", WhoAmIMemberView.as_view()),
    path("member/logout/", LogoutView.as_view()),
    path("member/refresh/", AuthRefreshView.as_view()),
    path("member/forgotpassword/", ForgotPasswordAdminView.as_view()),
    path("member/verifyforgotpassword/", VerifyForgotPasswordView.as_view()),
]

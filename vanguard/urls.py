from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from vanguard.api import (
    AuthRefreshView,
    WhoAmIView,
    AuthAdminLoginView,
    AuthLoginView,
    LogoutView,
    ForgotPasswordView,
    VerifyForgotPasswordView,
)

urlpatterns = [
    path("dblogin/", AuthAdminLoginView.as_view()),
    path("login/", AuthLoginView.as_view()),
    path("whoami/", WhoAmIView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("refresh/", AuthRefreshView.as_view()),
    path("forgotpassword/", ForgotPasswordView.as_view()),
    path("verifyforgotpassword/", VerifyForgotPasswordView.as_view()),
    path("forgotpassword/", ForgotPasswordView.as_view()),
    path("verifyforgotpassword/", VerifyForgotPasswordView.as_view()),
]

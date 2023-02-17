from rest_framework.routers import DefaultRouter
from accounts.api import (
    AccountListViewSet,
    AccountProfileViewSet,
    AccountAvatarViewSet,
    RegisterAccountView,
    VerifyRegistrationView,
    VerifyAccountView,
)
from django.urls import path

router = DefaultRouter()
router.register(r"getprofile", AccountProfileViewSet)
router.register(r"getmembers", AccountListViewSet)
router.register(r"getaccount", AccountAvatarViewSet)

urlpatterns = [
    path("verifyaccount/", VerifyAccountView.as_view()),
    # Members
    path("register/", RegisterAccountView.as_view()),
    path("verifyregistration/", VerifyRegistrationView.as_view()),
]

urlpatterns += router.urls

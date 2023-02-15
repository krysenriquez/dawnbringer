from rest_framework.routers import DefaultRouter
from accounts.api import (
    AccountProfileViewSet,
    AccountListViewSet,
    RegisterAccountView,
    VerifyRegistrationView,
    VerifyAccountView,
)
from django.urls import path

router = DefaultRouter()
router.register(r"getprofile", AccountProfileViewSet)
router.register(r"getmembers", AccountListViewSet)

urlpatterns = [
    path("register/", RegisterAccountView.as_view()),
    path("verifyregistration/", VerifyRegistrationView.as_view()),
    path("verifyaccount/", VerifyAccountView.as_view()),
]

urlpatterns += router.urls

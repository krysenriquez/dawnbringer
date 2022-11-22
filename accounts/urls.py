from rest_framework.routers import DefaultRouter
from accounts.api import (
    AccountProfileViewSet,
    AccountListViewSet,
    CreateAccountView,
    VerifyAccountView,
)
from django.urls import path

router = DefaultRouter()
router.register(r"getprofile", AccountProfileViewSet)
router.register(r"getmembers", AccountListViewSet)

urlpatterns = [
    path("create/", CreateAccountView.as_view()),
    path("verifyaccount/", VerifyAccountView.as_view()),
]

urlpatterns += router.urls

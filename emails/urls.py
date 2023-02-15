from rest_framework.routers import DefaultRouter
from django.urls import path
from emails.api import (
    Test,
)

router = DefaultRouter()

urlpatterns = [
    path("test/", Test.as_view()),
]

urlpatterns += router.urls

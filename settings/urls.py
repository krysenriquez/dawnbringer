from rest_framework.routers import DefaultRouter
from django.urls import path
from settings.api import BranchAssignmentsViewSet, BranchViewSet

router = DefaultRouter()
router.register(r"getbranchassignments", BranchAssignmentsViewSet)
router.register(r"getbranches", BranchViewSet)

urlpatterns = []

urlpatterns += router.urls

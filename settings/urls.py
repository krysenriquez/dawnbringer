from rest_framework.routers import DefaultRouter
from django.urls import path
from settings.api import BranchAssignmentsViewSet, BranchListViewSet

router = DefaultRouter()
router.register(r"getbranchassignments", BranchAssignmentsViewSet)
router.register(r"getbranches", BranchListViewSet)

urlpatterns = []

urlpatterns += router.urls

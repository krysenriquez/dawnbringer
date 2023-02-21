from rest_framework.routers import DefaultRouter
from django.urls import path
from settings.api import CompanyViewSet, BranchAssignmentsViewSet, BranchListViewSet

router = DefaultRouter()
router.register(r"getbranchassignments", BranchAssignmentsViewSet)
router.register(r"getbranches", BranchListViewSet)
router.register(r"getcompany", CompanyViewSet)

urlpatterns = []

urlpatterns += router.urls

from rest_framework.routers import DefaultRouter
from django.urls import path
from settings.api import (
    CompanyViewSet,
    BranchAssignmentsViewSet,
    BranchInfoViewSet,
    BranchListViewSet,
    CreateBranchView,
    UpdateBranchView,
)

router = DefaultRouter()
router.register(r"getbranchassignments", BranchAssignmentsViewSet)
router.register(r"getbranches", BranchListViewSet)
router.register(r"getbranch", BranchInfoViewSet)
router.register(r"getcompany", CompanyViewSet)

urlpatterns = [path("createbranch/", CreateBranchView.as_view()), path("updatebranch/", UpdateBranchView.as_view())]

urlpatterns += router.urls

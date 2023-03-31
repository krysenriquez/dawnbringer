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
# Admin
router.register(r"admin/getbranchassignments", BranchAssignmentsViewSet)
router.register(r"admin/getbranches", BranchListViewSet)
router.register(r"admin/getbranch", BranchInfoViewSet)
router.register(r"admin/getcompany", CompanyViewSet)
# Member
router.register(r"member/getcompany", CompanyViewSet)

urlpatterns = [
    # Admin
    path("admin/createbranch/", CreateBranchView.as_view()),
    path("admin/updatebranch/", UpdateBranchView.as_view()),
]

urlpatterns += router.urls

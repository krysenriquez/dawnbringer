from rest_framework.routers import DefaultRouter
from shop.api import PageContentsViewSet, PageComponentsViewSet

router = DefaultRouter()
router.register(r"getpagecontents", PageContentsViewSet)
router.register(r"getpagecomponents", PageComponentsViewSet)

urlpatterns = []

urlpatterns += router.urls

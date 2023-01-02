from rest_framework.routers import DefaultRouter
from shop.api import PageContentsViewSet, PageComponentsViewSet, SectionComponentsViewSet

router = DefaultRouter()
router.register(r"getpagecontents", PageContentsViewSet)
router.register(r"getpagecomponents", PageComponentsViewSet)
router.register(r"getsectioncomponents", SectionComponentsViewSet)

urlpatterns = []

urlpatterns += router.urls

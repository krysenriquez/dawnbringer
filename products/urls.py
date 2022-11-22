from rest_framework.routers import DefaultRouter
from products.api import ProductTypesViewSet, ProductsViewSet

router = DefaultRouter()
router.register(r"getproducttypes", ProductTypesViewSet)
router.register(r"getproduct", ProductsViewSet)

urlpatterns = []

urlpatterns += router.urls

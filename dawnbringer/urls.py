from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("dawnbringer/admin/", admin.site.urls),
    # APIs
    path("dbwebapi/accounts/", include("accounts.urls"), name="accounts"),
    path("dbwebapi/products/", include("products.urls"), name="products"),
    path("dbwebapi/orders/", include("orders.urls"), name="orders"),
    path("dbwebapi/v1/shop/", include("shop.urls"), name="shop"),
    path("dbwebapi/settings/", include("settings.urls"), name="settings"),
    path("dbwebapi/users/", include("users.urls"), name="users"),
    path("dbwebapi/vanguard/", include("vanguard.urls"), name="vanguard"),
    path("dbwebapi/emails/", include("emails.urls"), name="emails"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "La Reussi Admin"
admin.site.site_title = "La Reussi"
admin.site.index_title = "Welcome to La Reussi Admin"
admin.autodiscover()

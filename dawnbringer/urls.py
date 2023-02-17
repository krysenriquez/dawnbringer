from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("dawnbringer/admin/", admin.site.urls),
    # APIs
    path("dbwebapi/accounts/", include("accounts.urls"), name="accounts"),
    path("dbwebapi/core/", include("core.urls"), name="core"),
    path("dbwebapi/emails/", include("emails.urls"), name="emails"),
    path("dbwebapi/orders/", include("orders.urls"), name="orders"),
    path("dbwebapi/products/", include("products.urls"), name="products"),
    path("dbwebapi/settings/", include("settings.urls"), name="settings"),
    path("dbwebapi/users/", include("users.urls"), name="users"),
    path("dbwebapi/vanguard/", include("vanguard.urls"), name="vanguard"),
    path("dbwebapi/v1/shop/", include("shop.urls"), name="shop"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Le Reussi Admin"
admin.site.site_title = "Le Reussi"
admin.site.index_title = "Welcome to Le Reussi Admin"
admin.autodiscover()

from django.contrib import admin
from django.urls import path, include

from shopapp import urls as shopapp_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include(shopapp_urls)),
]

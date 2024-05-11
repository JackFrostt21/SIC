from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from .yasg import schema_view
from django.conf.urls.i18n import i18n_patterns
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.shortcuts import render


# custom 404 view
def custom_404(request, exception):
    return render(request, '404.html', status=404)


handler404 = custom_404

base_url = [
    path('bot/', TemplateView.as_view(template_name='base.html'), name='home'),
    # re_path('.*', TemplateView.as_view(template_name='base.html'), name='home'),  # / regexp
]

urlpatterns = [path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
               path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
               path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
               path('api-swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
               path('api-redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
               path('api/testing-testing_module/', include('app.educational_module.urls')),
               ] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + i18n_patterns(
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    prefix_default_language=True,
) + base_url

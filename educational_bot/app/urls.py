from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from .yasg import schema_view
from django.conf.urls.i18n import i18n_patterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.shortcuts import render

from app.educational_module.views import (
    CourseViewSet,
    TopicCourseViewSet,
    PdfView,
    MainTextView,
    bot_info_view,
    progress_view,
    trainingcourse_custom_view
)
from app.lightning.views import lightnings_custom_view, LightningDeleteView, send_lightning_view

# custom 404 view
def custom_404(request, exception):
    return render(request, "404.html", status=404)


handler404 = custom_404

base_url = [
    path("bot/", TemplateView.as_view(template_name="base.html"), name="home"),
    # re_path('.*', TemplateView.as_view(template_name='base.html'), name='home'),  # / regexp
]

urlpatterns = (
    [
        path('ru/send_lightning/<int:lightning_id>/', send_lightning_view, name='send_lightning'),
        path('ru/lightning/lightning/', lightnings_custom_view, name='lightnings_custom_view'),
        path('ru/educational_module/trainingcourse/', trainingcourse_custom_view, name='trainingcourse_custom_view'),
        # path('ru/app/trainingcourses/', trainingcourse_list, name='trainingcourse_list'),
        # path('ru/app/trainingcourse/<int:course_id>/', training_course_detail, name='training_course_detail'),
        path("ckeditor/", include("ckeditor_uploader.urls")),
        path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path(
            "api-swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "api-redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
        path("api/testing-testing_module/", include("app.educational_module.urls")),
        path("bot-info/", bot_info_view, name="bot_info"),
        path("progress/", progress_view, name="progress"),
        path('ru/lightning/', include('app.lightning.urls')),  # lightning
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + i18n_patterns(
        path("jet/", include("jet.urls", "jet")),
        path("jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
        path("", admin.site.urls),
        path("i18n/", include("django.conf.urls.i18n")),
        # path('app/', include('app.educational_module.urls')),
        # path('ru/', include('app.educational_module.urls')), ### тут
        prefix_default_language=True,
    )
    + base_url
)
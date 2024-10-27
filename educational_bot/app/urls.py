from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from app.educational_module.views import (
    bot_info_view,
    progress_view,
    trainingcourse_custom_view, user_list_view, user_update, question_list_view, answer_list_view, save_answer_view
)
from .yasg import schema_view


# custom 404 view
def custom_404(request, exception):
    return render(request, "404.html", status=404)


handler404 = custom_404

base_url = [
    path("bot/", TemplateView.as_view(template_name="base.html"), name="home"),
]

urlpatterns = (
        [
            path('ru/educational_module/trainingcourse/', trainingcourse_custom_view,
                 name='trainingcourse_custom_view'),
            path("ru/educational_module/user-card/", user_list_view, name='user_list'),
            path("ru/educational_module/user-card/update-user/", user_update, name='user_detail_update'),

            path("ru/educational_module/testing-card/", question_list_view, name='question_list'),
            path("ru/educational_module/testing-card/answer-list/<int:question_id>/", answer_list_view, name='answer_list'),
            path("ru/educational_module/testing-card/save-answer/<int:question_id>/", save_answer_view, name='answer_list'),

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
        ]
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + i18n_patterns(
    path("jet/", include("jet.urls", "jet")),
    path("jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
    path("", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),

    prefix_default_language=True,
)
        + base_url
)

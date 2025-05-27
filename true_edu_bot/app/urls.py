from rest_framework.routers import DefaultRouter
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
    PdfView,
    MainTextView,
    TagCourseViewSet,
    bot_info_view,
    progress_view,
    TrainingCourseViewSet,
    CourseTopicViewSet,
    CourseDirectionViewSet,
    TopicQuestionViewSet,
    AnswerOptionViewSet,
    TelegramUserViewSet,
    TelegramGroupViewSet,
    UserReadViewSet,
    UserTestViewSet,
    ScormPackViewSet,
    NewsBlockViewSet,
    CompanyViewSet,
    CertificateViewSet,
    RatingTrainingCourseViewSet,
    CourseDeadlineViewSet,
)
from app.reference_data.views import DepartmentViewSet, JobTitleViewSet

def custom_404(request, exception):
    return render(request, "404.html", status=404)

handler404 = custom_404

base_url = [
    path("bot/", TemplateView.as_view(template_name="base.html"), name="home"),
]

"""API для web версии проекта"""
router = DefaultRouter()
router.register(r'api/v1/trainingcourses', TrainingCourseViewSet, basename='web_trainingcourse')
router.register(r'api/v1/coursetopics', CourseTopicViewSet, basename='web_coursetopic')
router.register(r'api/v1/coursedirections', CourseDirectionViewSet, basename='web_coursedirection')
router.register(r'api/v1/topicquestions', TopicQuestionViewSet, basename='web_topicquestion')
router.register(r'api/v1/answeroptions', AnswerOptionViewSet, basename='web_answeroption')
router.register(r'api/v1/telegramusers', TelegramUserViewSet, basename='web_telegramuser')
router.register(r'api/v1/telegramgroups', TelegramGroupViewSet, basename='web_telegramgroup')
router.register(r'api/v1/userreads', UserReadViewSet, basename='web_userread')
router.register(r'api/v1/usertests', UserTestViewSet, basename='web_usertest')
router.register(r'api/v1/scormpacks', ScormPackViewSet, basename='web_scormpack')
router.register(r'api/v1/newsblock', NewsBlockViewSet, basename='web_newsblock')
router.register(r'api/v1/tagcourses', TagCourseViewSet, basename='web_newsblock')
router.register(r'api/v1/jobtitles', JobTitleViewSet, basename='web_jobtitle')
router.register(r'api/v1/departments', DepartmentViewSet, basename='web_department')
router.register(r'api/v1/companies', CompanyViewSet, basename='web_company')
router.register(r'api/v1/certificaties', CertificateViewSet, basename='web_certificate')
router.register(r'api/v1/ratingtrainingcourses', RatingTrainingCourseViewSet, basename='web_ratingtrainingcourse')
router.register(r'api/v1/coursedeadlines', CourseDeadlineViewSet, basename='web_coursedeadline')
"""API для web версии проекта"""


urlpatterns = (
    [
        # path('debug-template/', debug_view, name='debug-template'),
        path('', include(router.urls)),
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
        # path("jet/", include("jet.urls", "jet")),
        # path("jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
        path("", admin.site.urls),
        path("i18n/", include("django.conf.urls.i18n")),
        prefix_default_language=True,
    )
    + base_url
)

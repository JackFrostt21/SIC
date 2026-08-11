from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from app.learning_app.views import *
from app.bot.views import *
from app.organization.views import *
from app.web_views import *


# TODO: Добавить кастомную обработку ошибок (404)

"""API для web версии проекта"""
router = DefaultRouter()
router.register(
    r"api/v1/telegramusers", WebTelegramUserViewSet, basename="web_telegramuser"
)
router.register(
    r"api/v1/telegramgroups", WebTelegramGroupViewSet, basename="web_telegramgroup"
)
router.register(r"api/v1/customusers", WebCustomUserViewSet, basename="web_customuser")
router.register(r"api/v1/userreads", WebUserReadViewSet, basename="web_userread")
router.register(r"api/v1/usertests", WebUserTestViewSet, basename="web_usertest")
router.register(
    r"api/v1/trainingcourses", WebTrainingCourseViewSet, basename="web_trainingcourse"
)
router.register(
    r"api/v1/coursetopics", WebCourseTopicViewSet, basename="web_coursetopic"
)
router.register(
    r"api/v1/coursedirections",
    WebCourseDirectionViewSet,
    basename="web_coursedirection",
)
router.register(
    r"api/v1/topicquestions", WebTopicQuestionViewSet, basename="web_topicquestion"
)
router.register(
    r"api/v1/answeroptions", WebAnswerOptionViewSet, basename="web_answeroption"
)
router.register(r"api/v1/newsblock", WebNewsBlockViewSet, basename="web_newsblock")
router.register(r"api/v1/tagcourses", WebTagCourseViewSet, basename="web_tagcourse")
router.register(
    r"api/v1/certificaties", WebCertificateViewSet, basename="web_certificate"
)
router.register(
    r"api/v1/ratingtrainingcourses",
    WebRatingTrainingCourseViewSet,
    basename="web_ratingtrainingcourse",
)
router.register(
    r"api/v1/coursedeadlines", WebCourseDeadlineViewSet, basename="web_coursedeadline"
)
router.register(r"api/v1/jobtitles", WebJobTitleViewSet, basename="web_jobtitle")
router.register(r"api/v1/departments", WebDepartmentViewSet, basename="web_department")
router.register(r"api/v1/companies", WebCompanyViewSet, basename="web_company")
router.register(
    r"api/v1/settingsbot", WebSettingsBotViewSet, basename="web_settingsbot"
)
router.register(r"api/v1/user-rating", WebUserRatingViewSet, basename="web_userrating")
"""API для web версии проекта"""

urlpatterns = [
    path(
        "admin/statistics/education/",
        admin.site.admin_view(statistics_education_view),
        name="admin-statistics-education",
    ),
    path("admin/", admin.site.urls),
    path(
        "ckeditor5/", include("django_ckeditor_5.urls"), name="ck_editor_5_upload_file"
    ),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # path("bot-info/", bot_info_view, name="bot_info"), # TODO: Добавить бот-инфо
    # path("progress/", progress_view, name="progress"), # TODO: Добавить прогресс
    path("", include(router.urls)),
    path("", include("app.learning_app.urls")),
    # JWT Token (существующие endpoints)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Новые API endpoints для аутентификации
    path("api/auth/", include("app.bot.urls.auth_urls")),
    # API endpoints для тестирования курсов
    path("api/test/", include("app.bot.urls.test_urls")),
    # API endpoints для списка тестов пользователя
    path("api/testlist/", include("app.bot.urls.testlist_urls")),
    # API endpoints для чтения материалов
    path("api/read/", include("app.bot.urls.read_urls")),
    # API endpoints для статистики пользователей
    path("api/v1/", include("app.bot.urls.userstat_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

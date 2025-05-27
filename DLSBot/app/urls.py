from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from app.learning_app.views import *
from app.bot.views import *
from app.organization.views import *


# TODO: Добавить кастомную обработку ошибок (404)

# TODO: Подумать про Swagger

"""API для web версии проекта"""
router = DefaultRouter()
router.register(
    r"api/v1/telegramusers", TelegramUserViewSet, basename="web_telegramuser"
)
router.register(
    r"api/v1/telegramgroups", TelegramGroupViewSet, basename="web_telegramgroup"
)
router.register(r"api/v1/userreads", UserReadViewSet, basename="web_userread")
router.register(r"api/v1/usertests", UserTestViewSet, basename="web_usertest")
router.register(
    r"api/v1/trainingcourses", TrainingCourseViewSet, basename="web_trainingcourse"
)
router.register(r"api/v1/coursetopics", CourseTopicViewSet, basename="web_coursetopic")
router.register(
    r"api/v1/coursedirections", CourseDirectionViewSet, basename="web_coursedirection"
)
router.register(
    r"api/v1/topicquestions", TopicQuestionViewSet, basename="web_topicquestion"
)
router.register(
    r"api/v1/answeroptions", AnswerOptionViewSet, basename="web_answeroption"
)
router.register(r"api/v1/scormpacks", ScormPackViewSet, basename="web_scormpack")
router.register(r"api/v1/newsblock", NewsBlockViewSet, basename="web_newsblock")
router.register(r"api/v1/tagcourses", TagCourseViewSet, basename="web_tagcourse")
router.register(r"api/v1/certificaties", CertificateViewSet, basename="web_certificate")
router.register(
    r"api/v1/ratingtrainingcourses",
    RatingTrainingCourseViewSet,
    basename="web_ratingtrainingcourse",
)
router.register(
    r"api/v1/coursedeadlines", CourseDeadlineViewSet, basename="web_coursedeadline"
)
router.register(r"api/v1/jobtitles", JobTitleViewSet, basename="web_jobtitle")
router.register(r"api/v1/departments", DepartmentViewSet, basename="web_department")
router.register(r"api/v1/companies", CompanyViewSet, basename="web_company")
router.register(r"api/v1/settingsbot", SettingsBotViewSet, basename="web_settingsbot")
"""API для web версии проекта"""

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "ckeditor5/", include("django_ckeditor_5.urls"), name="ck_editor_5_upload_file"
    ),
    # path("bot-info/", bot_info_view, name="bot_info"), # TODO: Добавить бот-инфо
    # path("progress/", progress_view, name="progress"), # TODO: Добавить прогресс
    path("", include(router.urls)),
    path("", include("app.learning_app.urls")),

    # JWT Token
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

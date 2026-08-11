from django.urls import path, include
from . import views

urlpatterns = [
    path(
        "webapp/topic/<int:topic_pk>/text/",
        views.topic_text_webapp_view,
        name="webapp_topic_text",
    ),
    path(
        "webapp/bot-info/",
        views.bot_info_webapp_view,
        name="webapp_bot_info",
    ),
    path(
        "webapp/progress/",
        views.progress_webapp_view,
        name="webapp_progress",
    ),
    path(
        "api/v1/available-courses/",
        views.AvailableTrainingCourseView.as_view(),
        name="available_courses",
    ),
    path(
        "api/v1/trainingcourses/<int:course_id>/enroll/",
        views.EnrollTrainingCourseView.as_view(),
        name="enroll_training_course",
    ),
    path(
        "api/v1/scormpacks/",
        views.ScormPackFileView.as_view(),
        name="scorm_pack_file",
    ),
]

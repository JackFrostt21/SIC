from django.urls import path
from rest_framework import routers

from app.educational_module.views import (
    CourseViewSet,
    TopicCourseViewSet,
    PdfView,
    MainTextView,
    bot_info_view,
    progress_view,
    trainingcourse_custom_view,
    TrainingCourseDeleteView,
    groups_custom_view,
    add_student_to_group,
    remove_student_from_group,
)

router = routers.DefaultRouter()
router.register(r"course", CourseViewSet)
router.register(r"topic_course", TopicCourseViewSet)

urlpatterns = [
    *router.urls,
    path("trainingcourses/", trainingcourse_custom_view, name="trainingcourse_custom"),
    path(
        "trainingcourse/<int:course_id>/",
        trainingcourse_custom_view,
        name="trainingcourse_custom",
    ),
    path('trainingcourses/create/', trainingcourse_custom_view, name='trainingcourse_custom_create'),
    path('trainingcourse/<int:pk>/delete/', TrainingCourseDeleteView.as_view(), name='trainingcourse_delete'),
    path("course_topic/<int:pk>/pdf/", PdfView.as_view(), name="course_topic_pdf"),
    path(
        "course_topic/<int:pk>/main_text/",
        MainTextView.as_view(),
        name="course_topic_main_text",
    ),
    path("bot-info/", bot_info_view, name="bot_info"),
    path("progress/", progress_view, name="progress"),
    path("groups/", groups_custom_view, name="groups_custom"),
    path('add-student-to-group/', add_student_to_group, name='add_student_to_group'),
    path('remove-student-from-group/', remove_student_from_group, name='remove_student_from_group'),
]

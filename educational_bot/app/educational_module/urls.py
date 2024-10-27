from rest_framework import routers
from django.urls import path


from app.educational_module.views import (
    CourseViewSet,
    TopicCourseViewSet,
    PdfView,
    MainTextView,
    bot_info_view,
    progress_view,
    trainingcourse_custom_view,
    TrainingCourseDeleteView,
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
    # path('trainingcourse/delete/<int:course_id>/', trainingcourse_delete_view, name='trainingcourse_delete'),
    path('trainingcourse/<int:pk>/delete/', TrainingCourseDeleteView.as_view(), name='trainingcourse_delete'),
    path("course_topic/<int:pk>/pdf/", PdfView.as_view(), name="course_topic_pdf"),
    path(
        "course_topic/<int:pk>/main_text/",
        MainTextView.as_view(),
        name="course_topic_main_text",
    ),
    path("bot-info/", bot_info_view, name="bot_info"),
    path("progress/", progress_view, name="progress"),
]

from rest_framework import routers
from django.urls import path


from app.educational_module.views import (
    PdfView,
    MainTextView,
    bot_info_view,
    progress_view,
)

urlpatterns = [
    path("course_topic/<int:pk>/pdf/", PdfView.as_view(), name="course_topic_pdf"),
    path(
        "course_topic/<int:pk>/main_text/",
        MainTextView.as_view(),
        name="course_topic_main_text",
    ),
    path("bot-info/", bot_info_view, name="bot_info"),
    path("progress/", progress_view, name="progress"),
]

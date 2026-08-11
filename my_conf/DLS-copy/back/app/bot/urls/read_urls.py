from django.urls import path
from ..views.read_views import (
    CourseReadView,
    CourseReadSubmitView,
    UnfinishedCoursesView,
)

urlpatterns = [
    path(
        "users/<int:telegram_user_id>/courses/",
        CourseReadView.as_view(),
        name="course_read_list",
    ),
    path(
        "users/<int:telegram_user_id>/courses/<int:course_id>/topics/<int:topic_id>/mark-read/",
        CourseReadSubmitView.as_view(),
        name="course_read_submit",
    ),
    path(
        "users/<int:telegram_user_id>/unfinished-courses/",
        UnfinishedCoursesView.as_view(),
        name="unfinished_courses_list",
    ),
]

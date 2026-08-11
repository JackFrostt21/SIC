from django.urls import path
from ..views.test_views import (
    CourseTestView,
    CourseTestSubmitView,
    TopicTestView,
    TopicTestSubmitView,
)

urlpatterns = [
    path("courses/<int:course_id>/test/", CourseTestView.as_view(), name="course_test"),
    path(
        "courses/<int:course_id>/submit/",
        CourseTestSubmitView.as_view(),
        name="course_test_submit",
    ),
    path("topics/<int:topic_id>/test/", TopicTestView.as_view(), name="topic_test"),
    path(
        "topics/<int:topic_id>/submit/",
        TopicTestSubmitView.as_view(),
        name="topic_test_submit",
    ),
]

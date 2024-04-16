from rest_framework import routers

from app.educational_module.views import CourseViewSet, TopicCourseViewSet

router = routers.DefaultRouter()
router.register(r"course", CourseViewSet)
router.register(r"topic_course", TopicCourseViewSet)

urlpatterns = router.urls

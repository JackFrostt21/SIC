from rest_framework import viewsets
from .models import TrainingCourse, CourseTopic, TopicQuestion
from .serializer import CourseSerializer, TopicCourseSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    queryset = TrainingCourse.objects.all()
    permission_classes = []


class TopicCourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TopicCourseSerializer
    queryset = CourseTopic.objects.all()
    permission_classes = []

# class UserAnswerViewSet(viewsets.ModelViewSet):
#     serializer_class = UserAnswerSerializer
#     queryset = UserAnswer.objects.all()
#     permission_classes = []
#
#     def create(self, request, *args, **kwargs):
#
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid()
#
#         user = TelegramUser.objects.get(user_id=request.data["user_id"])
#         choice_id = serializer.initial_data["choice"]
#         question_id = serializer.initial_data["question"]
#
#         UserAnswer.objects.create(question_id=question_id, choice_id=choice_id)
#         # question = Question.objects.get(id=question_id)
#         #
#         # choice_all_id = question.choice_set.values_list("id", flat=True)
#         is_correct = AnswerOption.objects.get(id=choice_id).is_correct
#         test_id = TestQuestion.objects.get(id=question_id).test_id
#         test_course = TestOnTopic.objects.get(id=test_id).id
#
#         course_instance = TrainingCourse.objects.get(id=test_course)
#
#         if is_correct:
#             UserTestResult.objects.update_or_create(course=course_instance, user=user,
#                                                     defaults={'is_correct_answers': True})
#         else:
#             UserTestResult.objects.update_or_create(course=course_instance, user=user,
#                                                     defaults={'is_correct_answers': False})
#
#         return Response(data=serializer.data, status=200)

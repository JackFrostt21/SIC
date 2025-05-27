from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models.additional import (
    Certificate,
    RatingTrainingCourse,
    CourseDeadline,
    NewsBlock,
)
from .models.courses import (
    TagCourse,
    CourseDirection,
    TrainingCourse,
    CourseTopic,
    ScormPack,
)
from .models.testing import TopicQuestion, AnswerOption
from .serializer import (
    CertificateSerializer,
    RatingTrainingCourseSerializer,
    CourseDeadlineSerializer,
    NewsBlockSerializer,
    TagCourseSerializer,
    CourseDirectionSerializer,
    TrainingCourseSerializer,
    CourseTopicSerializer,
    ScormPackSerializer,
    TopicQuestionSerializer,
    AnswerOptionSerializer,
)


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class RatingTrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = RatingTrainingCourse.objects.all()
    serializer_class = RatingTrainingCourseSerializer


class CourseDeadlineViewSet(viewsets.ModelViewSet):
    queryset = CourseDeadline.objects.all()
    serializer_class = CourseDeadlineSerializer


class NewsBlockViewSet(viewsets.ModelViewSet):
    queryset = NewsBlock.objects.all()
    serializer_class = NewsBlockSerializer


class TagCourseViewSet(viewsets.ModelViewSet):
    queryset = TagCourse.objects.all()
    serializer_class = TagCourseSerializer


class CourseDirectionViewSet(viewsets.ModelViewSet):
    queryset = CourseDirection.objects.all()
    serializer_class = CourseDirectionSerializer


class TrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer


class CourseTopicViewSet(viewsets.ModelViewSet):
    queryset = CourseTopic.objects.all()
    serializer_class = CourseTopicSerializer


class ScormPackViewSet(viewsets.ModelViewSet):
    queryset = ScormPack.objects.all()
    serializer_class = ScormPackSerializer


class TopicQuestionViewSet(viewsets.ModelViewSet):
    queryset = TopicQuestion.objects.all()
    serializer_class = TopicQuestionSerializer


class AnswerOptionViewSet(viewsets.ModelViewSet):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer


def topic_text_webapp_view(request, topic_pk):
    topic = get_object_or_404(CourseTopic, pk=topic_pk)
    context = {
        "topic_title": topic.title,
        "topic_main_text": topic.main_text,
        "topic_image_url": (
            topic.image_course_topic.url
            if topic.image_course_topic and hasattr(topic.image_course_topic, "url")
            else None
        ),
    }
    return render(request, "webapp/topic_text_display.html", context)


# class PdfView(View):
#     def get(self, request, pk):
#         course_topic = get_object_or_404(CourseTopic, pk=pk)
#         pdf_file = course_topic.pdf_file
#         if pdf_file:
#             response = HttpResponse(pdf_file, content_type='application/pdf')
#             response['Content-Disposition'] = f'inline; filename="{pdf_file.name}"'
#             return response
#         else:
#             return HttpResponse("No PDF file found for this course topic.")


# class MainTextView(View):
#     def get(self, request, pk):
#         course_topic = get_object_or_404(CourseTopic, pk=pk)
#         context = {
#             'topic': course_topic,
#         }
#         return render(request, 'course_topic_main_text.html', context)


# def bot_info_view(request):
#     company_name = "ЭНГС"
#     try:
#         company_instance = Company.objects.get(name=company_name)
#     except Company.DoesNotExist:
#         return render(request, 'bot_info.html', {'error_message': 'Компания не найдена'})

#     current_year = datetime.now().year

#     image_url = company_instance.image_spravka_for_bot.url if company_instance.image_spravka_for_bot else None
#     print(f"URL изображения справки: {image_url}")

#     return render(request, 'bot_info.html', {
#         'company_name': company_instance.name,
#         'bot_spravka': company_instance.spravka_for_bot,
#         'bot_version': company_instance.version_bot,
#         'image_spravka_for_bot': image_url,
#         'current_year': current_year,
#     })

# def progress_view(request):
#     user_id = request.GET.get('user_id')

#     if not user_id:
#         return render(request, 'progress.html', {'error_message': 'ID пользователя не найден'})

#     try:
#         # Ищем пользователя по внутреннему ID
#         telegram_user = TelegramUser.objects.get(id=user_id)
#     except TelegramUser.DoesNotExist:
#         return render(request, 'progress.html', {'error_message': 'Пользователь не найден'})


#     training_ids = TrainingCourse.objects.filter(user=telegram_user).values_list("id", flat=True)
#     result_tests = UserTest.objects.filter(user=telegram_user, training__id__in=training_ids).order_by('training__title')

#     if not result_tests.exists():
#         return render(request, 'progress.html', {
#             'user': telegram_user,
#             'no_tests_message': 'Пользователь еще не выполнял тесты.'
#         })

#     tests = []
#     successful_tests = 0
#     total_tests = result_tests.count()

#     for result_test in result_tests:
#         course_name = result_test.training.title
#         result = result_test.quantity_correct
#         passed = "Да" if result_test.complete else "Нет"
#         passed_class = "success" if result_test.complete else "fail"

#         tests.append({
#             'course_name': course_name,
#             'result': result,
#             'passed': passed,
#             'passed_class': passed_class
#         })

#         if result_test.complete:
#             successful_tests += 1

#     all_tests_passed = successful_tests == total_tests

#     # Определяем путь к изображению в зависимости от результата
#     if all_tests_passed:
#         progress_image_url = telegram_user.company.image_progess_good.url if telegram_user.company.image_progess_good else None
#     else:
#         progress_image_url = telegram_user.company.image_progess_bad.url if telegram_user.company.image_progess_bad else None

#     return render(request, 'progress.html', {
#         'user': telegram_user,
#         'tests': tests,
#         'successful_tests': successful_tests,
#         'total_tests': total_tests,
#         'all_tests_passed': all_tests_passed,
#         'progress_image_url': progress_image_url,
#     })

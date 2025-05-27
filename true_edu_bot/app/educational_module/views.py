import json
from django.views.generic import View
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import TrainingCourse, CourseTopic, CourseDirection, TopicQuestion, AnswerOption, ScormPack, NewsBlock, TagCourse, Company, Certificate, RatingTrainingCourse, CourseDeadline
from app.bot.models.testing_module import UserTest
from app.bot.models.telegram_user import TelegramUser, TelegramGroup, UserRead
from .serializer import (
    TagCourseSerializer,
    TrainingCourseSerializer, 
    CourseTopicSerializer, 
    CourseDirectionSerializer,
    TopicQuestionSerializer,
    AnswerOptionSerializer,
    TelegramUserSerializer,
    TelegramGroupSerializer,
    UserReadSerializer,
    UserTestSerializer,
    ScormPackSerializer,
    NewsBlockSerializer,
    CompanySerializer,
    CertificateSerializer,
    RatingTrainingCourseSerializer,
    CourseDeadlineSerializer,
    )


class PdfView(View):
    def get(self, request, pk):
        course_topic = get_object_or_404(CourseTopic, pk=pk)
        pdf_file = course_topic.pdf_file
        if pdf_file:
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{pdf_file.name}"'
            return response
        else:
            return HttpResponse("No PDF file found for this course topic.")


class MainTextView(View):
    def get(self, request, pk):
        course_topic = get_object_or_404(CourseTopic, pk=pk)
        context = {
            'topic': course_topic,
        }
        return render(request, 'course_topic_main_text.html', context)


def bot_info_view(request):
    company_name = "ЭНГС"
    try:
        company_instance = Company.objects.get(name=company_name)
    except Company.DoesNotExist:
        return render(request, 'bot_info.html', {'error_message': 'Компания не найдена'})

    current_year = datetime.now().year

    image_url = company_instance.image_spravka_for_bot.url if company_instance.image_spravka_for_bot else None
    print(f"URL изображения справки: {image_url}")

    return render(request, 'bot_info.html', {
        'company_name': company_instance.name,
        'bot_spravka': company_instance.spravka_for_bot,
        'bot_version': company_instance.version_bot,
        'image_spravka_for_bot': image_url,
        'current_year': current_year,
    })

def progress_view(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return render(request, 'progress.html', {'error_message': 'ID пользователя не найден'})
    
    try:
        # Ищем пользователя по внутреннему ID
        telegram_user = TelegramUser.objects.get(id=user_id)
    except TelegramUser.DoesNotExist:
        return render(request, 'progress.html', {'error_message': 'Пользователь не найден'})


    training_ids = TrainingCourse.objects.filter(user=telegram_user).values_list("id", flat=True)
    result_tests = UserTest.objects.filter(user=telegram_user, training__id__in=training_ids).order_by('training__title')

    if not result_tests.exists():
        return render(request, 'progress.html', {
            'user': telegram_user,
            'no_tests_message': 'Пользователь еще не выполнял тесты.'
        })

    tests = []
    successful_tests = 0
    total_tests = result_tests.count()

    for result_test in result_tests:
        course_name = result_test.training.title
        result = result_test.quantity_correct
        passed = "Да" if result_test.complete else "Нет"
        passed_class = "success" if result_test.complete else "fail"

        tests.append({
            'course_name': course_name,
            'result': result,
            'passed': passed,
            'passed_class': passed_class
        })

        if result_test.complete:
            successful_tests += 1

    all_tests_passed = successful_tests == total_tests

    # Определяем путь к изображению в зависимости от результата
    if all_tests_passed:
        progress_image_url = telegram_user.company.image_progess_good.url if telegram_user.company.image_progess_good else None
    else:
        progress_image_url = telegram_user.company.image_progess_bad.url if telegram_user.company.image_progess_bad else None

    return render(request, 'progress.html', {
        'user': telegram_user,
        'tests': tests,
        'successful_tests': successful_tests,
        'total_tests': total_tests,
        'all_tests_passed': all_tests_passed,
        'progress_image_url': progress_image_url,
    })

'----------------------------------For API WEB--------------------------------------'

class TrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer


class CourseTopicViewSet(viewsets.ModelViewSet):
    queryset = CourseTopic.objects.all()
    serializer_class = CourseTopicSerializer


class CourseDirectionViewSet(viewsets.ModelViewSet):
    queryset = CourseDirection.objects.all()
    serializer_class = CourseDirectionSerializer


class TopicQuestionViewSet(viewsets.ModelViewSet):
    queryset = TopicQuestion.objects.all()
    serializer_class = TopicQuestionSerializer        


class AnswerOptionViewSet(viewsets.ModelViewSet):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer


class TelegramGroupViewSet(viewsets.ModelViewSet):
    queryset = TelegramGroup.objects.all()
    serializer_class = TelegramGroupSerializer


class UserReadViewSet(viewsets.ModelViewSet):
    queryset = UserRead.objects.all()
    serializer_class = UserReadSerializer


class UserTestViewSet(viewsets.ModelViewSet):
    queryset = UserTest.objects.all()
    serializer_class = UserTestSerializer


class ScormPackViewSet(viewsets.ModelViewSet):
    queryset = ScormPack.objects.all()
    serializer_class = ScormPackSerializer


class NewsBlockViewSet(viewsets.ModelViewSet):
    queryset = NewsBlock.objects.all()
    serializer_class = NewsBlockSerializer


class TagCourseViewSet(viewsets.ModelViewSet):
    queryset = TagCourse.objects.all()
    serializer_class = TagCourseSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class RatingTrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = RatingTrainingCourse.objects.all()
    serializer_class = RatingTrainingCourseSerializer


class CourseDeadlineViewSet(viewsets.ModelViewSet):
    queryset = CourseDeadline.objects.all()
    serializer_class = CourseDeadlineSerializer
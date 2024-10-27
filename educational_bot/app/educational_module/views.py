import json
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.edit import DeleteView
from rest_framework import viewsets

from app.bot.models.telegram_user import TelegramUser, TelegramGroup
from app.bot.models.testing_module import UserTest
from .models import TrainingCourse, CourseTopic, Company, CourseDirection, TopicQuestion, AnswerOption
from .serializer import CourseSerializer, TopicCourseSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    queryset = TrainingCourse.objects.all()
    permission_classes = []


class TopicCourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TopicCourseSerializer
    queryset = CourseTopic.objects.all()
    permission_classes = []


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
    company_instance = Company.objects.get(name=company_name)

    current_year = datetime.now().year

    return render(request, 'bot_info.html', {
        'company_name': company_instance.name,
        'bot_spravka': company_instance.spravka_for_bot,
        'bot_version': company_instance.version_bot,
        'image_spravka_for_bot': company_instance.image_spravka_for_bot,
        'current_year': current_year,
    })


def progress_view(request):
    telegram_user_id = request.GET.get('user_id')
    if not telegram_user_id:
        return render(request, 'error.html', {'message': 'Telegram ID пользователя не найден'})

    try:
        telegram_user = TelegramUser.objects.get(user_id=telegram_user_id)
        print(f"Найден пользователь: {telegram_user}")  # Отладочный вывод
    except TelegramUser.DoesNotExist:
        return render(request, 'error.html', {'message': 'Пользователь не найден'})

    training_ids = TrainingCourse.objects.filter(user=telegram_user).values_list("id", flat=True)
    result_tests = UserTest.objects.filter(user=telegram_user, training__id__in=training_ids).order_by(
        'training__title')

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

    return render(request, 'progress.html', {
        'user': telegram_user,
        'tests': tests,
        'successful_tests': successful_tests,
        'total_tests': total_tests,
        'all_tests_passed': all_tests_passed
    })


# def trainingcourse_list(request):
#     courses = TrainingCourse.objects.order_by('title')
#     return render(request, 'courses/trainingcourse_list.html', {'courses': courses})


# def training_course_detail(request, course_id):
#     courses = get_object_or_404(TrainingCourse, id=course_id)
#     return render(request, 'courses/training_course_detail.html', {'courses': courses})

def trainingcourse_custom_view(request, course_id=None):
    courses = TrainingCourse.objects.all()  # Получаем список всех курсов
    directions = CourseDirection.objects.all()  # Получаем все направления

    course = None
    if 'create' in request.path:
        course = TrainingCourse()  # Создаем новый пустой объект курса
    elif course_id:
        course = get_object_or_404(TrainingCourse, id=course_id)

    # Получаем всех студентов, которые еще не привязаны к данному курсу
    if course and course.pk:
        students = TelegramUser.objects.exclude(id__in=course.user.all())
        groups = TelegramGroup.objects.exclude(id__in=course.group.all())
    else:
        students = TelegramUser.objects.all()  # Если курс не выбран, показываем всех студентов
        groups = TelegramGroup.objects.all()  # Если курс не выбран, показываем все группы

    # Фильтруем разделы без курса
    topics = CourseTopic.objects.filter(training_course__isnull=True)

    if request.method == "POST" and course:
        course.title = request.POST.get('title')
        course.archive = request.POST.get('archive') == 'on'
        course.is_actual = request.POST.get('is_actual') == 'on'

        # Получаем объект CourseDirection по ID
        direction_id = request.POST.get('course_direction')
        if direction_id:
            course.course_direction = get_object_or_404(CourseDirection, id=direction_id)

        course.author = request.POST.get('author')
        course.description = request.POST.get('description')

        # Если изображение было загружено
        if 'image_course' in request.FILES:
            course.image_course = request.FILES['image_course']

        # Проверка на удаление изображения
        if request.POST.get('remove_image') == '1':
            course.image_course.delete(save=False)  # Удаление файла изображения
            course.image_course = None  # Сброс поля

        course.save()  # Сохраняем изменения в базе данных

        # Сохраняем ManyToMany отношения:
        # 1. Студенты
        selected_students = request.POST.getlist('students')  # Получаем список выбранных студентов
        for student_id in selected_students:
            student = TelegramUser.objects.get(id=student_id)
            course.user.add(student)  # Добавляем студентов, не затрагивая уже существующих

        # 2. Группы
        selected_groups = request.POST.getlist('groups')  # Получаем список выбранных групп
        for group_id in selected_groups:
            group = TelegramGroup.objects.get(id=group_id)
            course.group.add(group)  # Добавляем группы, не затрагивая уже существующих

        # 3. Разделы
        selected_topics = request.POST.getlist('topics')  # Получаем список выбранных разделов
        for topic_id in selected_topics:
            topic = CourseTopic.objects.get(id=topic_id)
            topic.training_course = course
            topic.save()

        return redirect('trainingcourse_custom', course_id=course.id)

    return render(request, 'courses/trainingcourse_custom.html', {
        'courses': courses,
        'course': course,  # Это может быть None, если курс не выбран
        'directions': directions,  # Передаем направления в шаблон
        'students': students,  # Студенты без связи с курсом
        'groups': groups,  # Группы без связи с курсом
        'topics': topics,  # Разделы без привязки к курсу
    })


class TrainingCourseDeleteView(DeleteView):
    model = TrainingCourse
    template_name = 'courses/trainingcourse_confirm_delete.html'
    success_url = reverse_lazy('trainingcourse_custom')


'----------------------------------kabul dev--------------------------------------'

from django.shortcuts import render


def user_list_view(request):
    users = TelegramUser.objects.all().exclude(user_name=None)
    context = {"users": users}
    return render(request, template_name='users/user_card.html', context=context)


def user_update(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = TelegramUser.objects.get(user_id=data["telegram_id"])
        user.phone = data["phone"]
        user.email = data["email"]
        user.last_name = data["last_name"]
        user.first_name = data["last_name"]
        user.middle_name = data["middle_name"]
        user.company = Company.objects.get(name=data["organization"])
        user.username = data["username"]
        user.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def question_list_view(request):
    questions = TopicQuestion.objects.all()
    context = {"questions": questions}
    return render(request=request, template_name='courses/testing_card.html', context=context)


def answer_list_view(request, question_id):
    answers = AnswerOption.objects.filter(topic_question__id=question_id)

    answers_data = []
    for answer in answers:
        answers_data.append({
            'id': answer.id,
            'text': answer.text,
            'correct': answer.is_correct,
        })

    return JsonResponse(answers_data, safe=False)


def save_answer_view(request, question_id):
    answer = AnswerOption.objects.filter(topic_question__id=question_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        answers = data.get('answers', [])

        for answer in answers:
            answer.text = answer.get('text')
            answers.correct = answer.get('correct')
            answers.save()

        return JsonResponse({'status': 'success'}, status=200)

    return JsonResponse({'status': 'failed'}, status=400)

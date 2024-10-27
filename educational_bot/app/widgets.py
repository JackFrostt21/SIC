from jet.dashboard.modules import DashboardModule
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from django.db.models import Count, Q, F, Subquery, OuterRef, Avg, Value
from django.db.models.functions import Coalesce
from app.bot.models.telegram_user import TelegramUser
from app.bot.models.testing_module import UserTest
from app.educational_module.models import TrainingCourse, CourseTopic, Subtopic, TopicQuestion, AnswerOption


def fixed_digits(num_obj, digits=0):
    return f"{num_obj:.{digits}f}"


class NumberOfCourseWidget(DashboardModule):
    title = _('Количество учащихся на курсе')

    collapsible = True
    contrast = False

    def render(self, request=None):
        # Получаем список всех курсов с количеством уникальных пользователей
        courses = TrainingCourse.objects.all()

        formatted_courses = []

        for course in courses:
            # Получаем уникальные идентификаторы пользователей, записанных на курс
            user_ids = course.user.values_list('id', flat=True)
            group_user_ids = course.group.values_list('users__id', flat=True)

            # Объединяем списки пользователей и удаляем дубли
            all_user_ids = set(user_ids).union(set(group_user_ids))

            # Количество уникальных пользователей
            total_user_count = len(all_user_ids)

            formatted_courses.append({
                'course_name': course.title,
                'total_user_count': total_user_count
            })

        context = {
            'courses': formatted_courses
        }
        return render_to_string('widgets/NumberOfCourse.html', context)


class AverageScoreWidget(DashboardModule):
    title = _('Average Score per Course')

    collapsible = True
    contrast = False

    def render(self, request=None):
        # Получаем список всех курсов с агрегированным средним значением правильных ответов
        courses = TrainingCourse.objects.annotate(average_correct=Avg('usertest__quantity_correct')).order_by('title')

        formatted_courses = []

        for course in courses:
            # Округляем средний процент правильных ответов до целого числа, если он есть, иначе ставим 0
            average_correct = round(course.average_correct) if course.average_correct else 0

            formatted_courses.append({
                'course_name': course.title,
                'average_correct': average_correct
            })

        # Сортировка по среднему проценту правильных ответов в порядке убывания
        formatted_courses.sort(key=lambda x: x['average_correct'], reverse=True)

        context = {
            'courses': formatted_courses
        }
        return render_to_string('widgets/AverageScoreWidget.html', context)


class TotalUserInfoWidget(DashboardModule):
    title = _('Total User Info')
    collapsible = True
    contrast = False

    user_count = []  # Общее число пользователей прошедших тесты.
    total_users = []  # Количество пользователей в зависимости от оценок.

    def render(self, request=None):
        try:
            context = {
                'item_quantity': [
                    {'users': 119, 'rang': 'Оценка 1'},
                    {'users': 12, 'rang': 'Оценка 2'},
                    {'users': 133, 'rang': 'Оценка 3'},
                    {'users': 50, 'rang': 'Оценка 4'},
                    {'users': 44, 'rang': 'Оценка 5'},
                    {'users': 156, 'rang': 'Оценка 6'}],
                'item_weight': [
                    {'users': 119, 'rang': 'Оценка 1'},
                    {'users': 12, 'rang': 'Оценка 2'},
                    {'users': 133, 'rang': 'Оценка 3'},
                    {'users': 50, 'rang': 'Оценка 4'},
                    {'users': 44, 'rang': 'Оценка 5'},
                    {'users': 156, 'rang': 'Оценка 6'}]
            }
            return render_to_string('widgets/total_user_info.html', context)
        except Exception as e:
            print(e)

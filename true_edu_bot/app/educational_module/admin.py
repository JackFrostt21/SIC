from django import forms
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html
from django.forms import ModelForm
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.http import HttpResponse
from tablib import Dataset
import pandas as pd
from solo.admin import SingletonModelAdmin

from app.educational_module.models import (Certificate, RatingTrainingCourse, RegistrationSetting, 
                                           TrainingCourse, 
                                           CourseTopic, 
                                           TopicQuestion, 
                                           AnswerOption, 
                                           Subtopic, 
                                           Company, 
                                           CourseDirection, 
                                           ScormPack, 
                                           NewsBlock,
                                           TagCourse,
                                           CourseDeadline,)
from app.bot.models.testing_module import UserTest
from app.bot.models.telegram_user import UserRead, TelegramUser
from .forms import ExcelImportForm


class SubtopicInlineAdmin(admin.StackedInline):
    model = Subtopic
    extra = 0


class AnswerOptionInlineAdmin(admin.StackedInline):
    model = AnswerOption
    extra = 0


class CourseTopicInlineAdmin(admin.StackedInline):
    model = CourseTopic
    extra = 0
    readonly_fields = ["more_info"]


class TopicQuestionInlineAdmin(admin.StackedInline):
    model = TopicQuestion
    extra = 0
    readonly_fields = ["more_info"]


def import_questions_view(request):
    course_id = request.session.get('import_course_id')
    if not course_id:
        return redirect('..')

    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                excel_file = request.FILES['excel_file']
                data = pd.read_excel(excel_file, engine='openpyxl')
                
                if len(data.columns) < 5:
                    form.add_error(None, "Файл должен содержать как минимум 5 столбцов")
                    return render(request, 'admin/excel_import.html', {'form': form})

                question_column = data.columns[0]
                answer_columns = data.columns[1:5]

                for index, row in data.iterrows():
                    question_title = row[question_column]
                    answers = [str(row[col]) if pd.notna(row[col]) else '' for col in answer_columns]
                    question, created = TopicQuestion.objects.get_or_create(title=question_title, training_id=course_id)
                    for i, answer_text in enumerate(answers):
                        is_correct = '*' in answer_text
                        answer_text = answer_text.replace('*', '').strip()
                        AnswerOption.objects.create(
                            topic_question=question,
                            number=str(i + 1),
                            text=answer_text,
                            is_correct=is_correct
                        )
                return redirect('..')
            except Exception as e:
                print(f"Ошибка: {e}")
                form.add_error(None, f"Ошибка при импорте данных: {e}")
    else:
        form = ExcelImportForm()
    return render(request, 'admin/excel_import.html', {'form': form})


# Функция для экспорта данных в Excel
def export_users_to_excel(modeladmin, request, queryset):
    dataset = Dataset()
    dataset.headers = ['User', 'Quantity Correct', 'Complete', 'Read Status']

    for course in queryset:
        user_tests = UserTest.objects.filter(training=course)
        for test in user_tests:
            read_status = get_read_status(test.user, course)
            dataset.append([
                test.user,
                test.quantity_correct,
                test.complete,
                read_status,
            ])

    response = HttpResponse(dataset.export('xlsx'), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
    return response

# Функция для вычисления статуса прочтения
def get_read_status(user, course):
    total_topics = CourseTopic.objects.filter(training_course=course).count()
    read_topics = UserRead.objects.filter(course=course, user=user, is_read=True).count()
    if total_topics == 0:
        return "Нет данных"
    return f"{read_topics}/{total_topics}"


class CompletedUsersInlineAdmin(admin.TabularInline):
    model = UserTest
    fields = ('user', 'quantity_correct', 'complete', 'read_status')
    readonly_fields = ('user', 'quantity_correct', 'complete', 'read_status')
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ищем пользователей, записанных на курс лично
        if 'object_id' in request.resolver_match.kwargs:  # Проверка наличия 'object_id' в kwargs
            course_id = request.resolver_match.kwargs['object_id']
            course = self.parent_model.objects.get(pk=course_id)
            user_ids = course.user.values_list('id', flat=True)
            
            # Ищем пользователей, записанных на курс через группы
            group_user_ids = course.group.values_list('users__id', flat=True)

            # Объединяем списки пользователей и удаляем дубли
            all_user_ids = set(user_ids).union(set(group_user_ids))
            # Получаем queryset для всех уникальных пользователей
            return UserTest.objects.filter(user__id__in=all_user_ids)
        else:  # Если 'object_id' отсутствует, вернуть пустой набор
            return self.model.objects.none()

    def read_status(self, instance):
        course = instance.training
        user = instance.user
        total_topics = CourseTopic.objects.filter(training_course=course).count()
        read_topics = UserRead.objects.filter(course=course, user=user, is_read=True).count()
        if total_topics == 0:
            return "Нет данных"
        return f"{read_topics}/{total_topics}"
    read_status.short_description = 'Статус чтения'


class CourseTopicAdminForm(forms.ModelForm):
    class Meta:
        model = CourseTopic
        fields = '__all__'
        widgets = {
            'main_text': CKEditorWidget(),
        }


class TrainingCourseForm(forms.ModelForm):  # обозначить что блокировка добавления на не актуальный курс только после сохранения
    class Meta:
        model = TrainingCourse
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and not self.instance.is_actual:
            self.fields['user'].disabled = True
            self.fields['group'].disabled = True


@admin.register(TrainingCourse)
class TrainingCourseModeAdmin(admin.ModelAdmin):
    form = TrainingCourseForm
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('title',)
    inlines = [CourseTopicInlineAdmin, TopicQuestionInlineAdmin, CompletedUsersInlineAdmin]
    actions = [export_users_to_excel, 'import_questions_action']

    # raw_id_fields = ('user', 'group')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-questions/', self.admin_site.admin_view(import_questions_view), name='import-questions'),
        ]
        return custom_urls + urls

    def import_questions_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Пожалуйста, выберите один курс для импорта вопросов.")
            return redirect('..')
        course_id = queryset.first().id
        request.session['import_course_id'] = course_id
        return redirect('admin:import-questions')

    import_questions_action.short_description = 'Импортировать вопросы из Excel'


@admin.register(CourseTopic)
class CourseTopicModeAdmin(admin.ModelAdmin):
    form = CourseTopicAdminForm
    list_display = ('training_course', 'title')
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('title',)
    inlines = [SubtopicInlineAdmin]


@admin.register(TopicQuestion)
class TopicQuestionModeAdmin(admin.ModelAdmin):
    list_display = ('training', 'title')
    list_display_links = ('training', 'title')
    search_fields = ('title',)
    list_filter = ('training', 'title',)
    inlines = [AnswerOptionInlineAdmin]  


@admin.register(Company)
class CompanyModeAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', )
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

    def logo_preview(self, obj):
        if obj.logo_company:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;"/>', obj.logo_company.url)
        return "-"
    logo_preview.short_description = 'Logo'


@admin.register(CourseDirection)
class CourseDirectionModeAdmin(admin.ModelAdmin):
    list_display = ('title', )
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('title',)


@admin.register(ScormPack)
class ScormPackModeAdmin(admin.ModelAdmin):
    list_display = ('training_course', )
    list_display_links = ('training_course',)
    search_fields = ('training_course',)
    list_filter = ('training_course',)


@admin.register(NewsBlock)
class NewsBlockModeAdmin(admin.ModelAdmin):
    list_display = ('news_title', )
    list_display_links = ('news_title',)
    search_fields = ('text_news', 'news_title')
    list_filter = ('text_news', 'news_title')


@admin.register(TagCourse)
class TagCourseModeAdmin(admin.ModelAdmin):
    list_display = ('tag_name', )
    list_display_links = ('tag_name',)
    search_fields = ('tag_name',)
    list_filter = ('tag_name',)


@admin.register(Certificate)
class CertificateModeAdmin(admin.ModelAdmin):
    list_display = ('result', ) #поменять
    list_display_links = ('result',)
    search_fields = ('result',)
    list_filter = ('result',)


@admin.register(RatingTrainingCourse)
class RatingTrainingCourseModeAdmin(admin.ModelAdmin):
    list_display = ('rating', ) #поменять
    list_display_links = ('rating',)
    search_fields = ('rating',)
    list_filter = ('rating',)


@admin.register(CourseDeadline)
class CourseDeadlineModeAdmin(admin.ModelAdmin):
    list_display = ('deadline_date', ) #поменять
    list_display_links = ('deadline_date',)
    search_fields = ('deadline_date',)
    list_filter = ('deadline_date',)


@admin.register(RegistrationSetting)
class RegistrationSettingAdmin(SingletonModelAdmin):
    pass
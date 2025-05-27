from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    TagCourse, CourseDirection, TrainingCourse, CourseTopic,
    TopicQuestion, AnswerOption, Certificate, 
    RatingTrainingCourse, CourseDeadline, NewsBlock
)


@admin.register(TagCourse)
class TagCourseAdmin(admin.ModelAdmin):
    list_display = ('tag_name', 'is_actual')
    search_fields = ('tag_name',)
    list_filter = ('is_actual',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CourseDirection)
class CourseDirectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_actual')
    search_fields = ('title',)
    list_filter = ('is_actual',)
    readonly_fields = ('created_at', 'updated_at')


class CourseTopicInline(admin.TabularInline):
    model = CourseTopic
    extra = 0
    fields = ('title', 'is_actual', 'more_info')
    readonly_fields = ('more_info',)
    show_change_link = True


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_direction', 'archive', 'is_actual', 'min_test_percent_course', 'users_count', 'display_image')
    list_filter = ('archive', 'is_actual', 'course_direction', 'tag')
    search_fields = ('title', 'description', 'author')
    filter_horizontal = ('tag', 'user', 'group')
    inlines = [CourseTopicInline]
    readonly_fields = ('created_at', 'updated_at', 'display_image')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'author', 'archive', 'is_actual', 'created_at', 'updated_at')
        }),
        ('Настройки курса', {
            'fields': ('course_direction', 'tag', 'min_test_percent_course', 'image_course', 'display_image')
        }),
        ('Доступ', {
            'fields': ('user', 'group')
        }),
    )
    
    def users_count(self, obj):
        return obj.user.count()
    
    users_count.short_description = "Кол-во студентов"
    
    def display_image(self, obj):
        if obj.image_course:
            return mark_safe(f'<img src="{obj.image_course.url}" width="150" />')
        return "Нет изображения"
    
    display_image.short_description = "Предпросмотр"


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 1
    fields = ('order', 'text', 'is_correct', 'is_actual')


@admin.register(CourseTopic)
class CourseTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'training_course', 'has_content', 'is_actual')
    list_filter = ('is_actual', 'training_course', 'main_text_readuser', 'pdf_file_readuser')
    search_fields = ('title', 'description', 'main_text')
    readonly_fields = ('created_at', 'updated_at', 'display_image')
    fieldsets = (
        ('Основная информация', {
            'fields': ('training_course', 'order', 'title', 'description', 'is_actual', 'created_at', 'updated_at')
        }),
        ('Основной контент', {
            'fields': ('main_text', 'image_course_topic', 'display_image')
        }),
        ('Файлы и медиа', {
            'classes': ('collapse',),
            'fields': ('pdf_file', 'audio_file', 'video_file')
        }),
        ('Настройки отображения в боте', {
            'classes': ('collapse',),
            'fields': (
                'main_text_readuser', 'main_text_webapp_readuser',
                'pdf_file_readuser', 'audio_file_readuser', 'video_file_readuser'
            )
        }),
    )
    
    def has_content(self, obj):
        has_main = bool(obj.main_text)
        has_pdf = bool(obj.pdf_file)
        has_audio = bool(obj.audio_file)
        has_video = bool(obj.video_file)
        
        content_parts = []
        if has_main:
            content_parts.append(format_html('<span style="color: green;">Текст</span>'))
        if has_pdf:
            content_parts.append(format_html('<span style="color: blue;">PDF</span>'))
        if has_audio:
            content_parts.append(format_html('<span style="color: purple;">Аудио</span>'))
        if has_video:
            content_parts.append(format_html('<span style="color: red;">Видео</span>'))
        
        if not content_parts:
            return format_html('<span style="color: gray;">Нет</span>')
        
        return mark_safe(' | '.join(content_parts))
    
    has_content.short_description = "Содержимое"
    
    def display_image(self, obj):
        if obj.image_course_topic:
            return mark_safe(f'<img src="{obj.image_course_topic.url}" width="150" />')
        return "Нет изображения"
    
    display_image.short_description = "Предпросмотр"


@admin.register(TopicQuestion)
class TopicQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'training', 'is_multiple_choice', 'order', 'is_actual', 'answer_count')
    list_filter = ('is_actual', 'training', 'is_multiple_choice')
    search_fields = ('title', 'training__title')
    list_editable = ('order',)
    inlines = [AnswerOptionInline]
    readonly_fields = ('created_at', 'updated_at')
    
    def answer_count(self, obj):
        count = obj.answer_options.count()
        correct = obj.answer_options.filter(is_correct=True).count()
        return format_html(
            '{} (правильных: <span style="color: green;">{}</span>)',
            count, correct
        )
    
    answer_count.short_description = "Варианты ответов"


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('order', 'text_short', 'topic_question', 'is_correct', 'is_actual')
    list_filter = ('is_actual', 'is_correct', 'topic_question__training')
    search_fields = ('text', 'topic_question__title', 'topic_question__training__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def text_short(self, obj):
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text
    
    text_short.short_description = "Текст ответа"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'training_course', 'result', 'created_at', 'has_file')
    list_filter = ('created_at', 'training_course')
    search_fields = ('user__full_name', 'user__user_name', 'training_course__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    def has_file(self, obj):
        return bool(obj.certificate_file)
    
    has_file.boolean = True
    has_file.short_description = "Файл"


@admin.register(RatingTrainingCourse)
class RatingTrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('student', 'training_course', 'rating_stars', 'created_at')
    list_filter = ('rating', 'training_course', 'created_at')
    search_fields = ('student__full_name', 'student__user_name', 'training_course__title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    
    rating_stars.short_description = "Оценка"


@admin.register(CourseDeadline)
class CourseDeadlineAdmin(admin.ModelAdmin):
    list_display = ('training_course', 'deadline_date', 'groups_count', 'users_count', 'is_past')
    list_filter = ('deadline_date', 'training_course')
    search_fields = ('training_course__title',)
    filter_horizontal = ('deadline_groups', 'deadline_users')
    date_hierarchy = 'deadline_date'
    readonly_fields = ('created_at', 'updated_at')
    
    def groups_count(self, obj):
        return obj.deadline_groups.count()
    
    groups_count.short_description = "Кол-во групп"
    
    def users_count(self, obj):
        return obj.deadline_users.count()
    
    users_count.short_description = "Кол-во студентов"
    
    def is_past(self, obj):
        from django.utils import timezone
        return obj.deadline_date < timezone.now().date()
    
    is_past.boolean = True
    is_past.short_description = "Наступил"


@admin.register(NewsBlock)
class NewsBlockAdmin(admin.ModelAdmin):
    list_display = ('news_title', 'start_date_news', 'end_date_news', 'is_published', 'is_actual', 'is_active')
    list_filter = ('is_actual', 'is_published', 'start_date_news', 'end_date_news')
    search_fields = ('news_title', 'text_news')
    date_hierarchy = 'start_date_news'
    readonly_fields = ('created_at', 'updated_at', 'display_image')
    fieldsets = (
        ('Основная информация', {
            'fields': ('news_title', 'text_news', 'is_published', 'is_actual')
        }),
        ('Сроки публикации', {
            'fields': ('start_date_news', 'end_date_news')
        }),
        ('Изображение', {
            'fields': ('image', 'display_image')
        }),
    )
    
    def is_active(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        is_started = obj.start_date_news <= today
        is_not_ended = obj.end_date_news is None or obj.end_date_news >= today
        return is_started and is_not_ended and obj.is_published
    
    is_active.boolean = True
    is_active.short_description = "Активна"
    
    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" />')
        return "Нет изображения"
    
    display_image.short_description = "Предпросмотр"
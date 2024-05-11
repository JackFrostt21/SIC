from django.contrib import admin
from app.educational_module.models import TrainingCourse, CourseTopic, TopicQuestion, AnswerOption, Subtopic


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


@admin.register(TrainingCourse)
class TrainingCourseModeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('title',)
    search_fields = ('id', 'title')
    list_filter = ('id', 'title')
    inlines = [CourseTopicInlineAdmin]


@admin.register(CourseTopic)
class CourseTopicModeAdmin(admin.ModelAdmin):
    list_display = ('training_course', 'title')
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('title',)
    inlines = [SubtopicInlineAdmin, TopicQuestionInlineAdmin]


@admin.register(TopicQuestion)
class TopicQuestionModeAdmin(admin.ModelAdmin):
    list_display = ('topic', 'title')
    list_display_links = ('topic', 'title')
    search_fields = ('title',)
    list_filter = ('title',)
    inlines = [AnswerOptionInlineAdmin]

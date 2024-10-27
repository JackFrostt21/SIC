from django.contrib import admin

from app.lightning.models import JobTitle, Lightning, LightningMessage, LightningQuestion, LightningAnswer


@admin.register(Lightning)
class LightningAdmin(admin.ModelAdmin):
    list_display = ('title', 'incident_location', 'created_at')
    search_fields = ('title',)


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(LightningMessage)
class LightningMessageAdmin(admin.ModelAdmin):
    list_display = ('lightning', 'content', 'send_text', 'send_file')
    search_fields = ('lightning__title',)


@admin.register(LightningQuestion)
class LightningQuestionAdmin(admin.ModelAdmin):
    list_display = ('lightning', 'title', 'is_multiple_choice', 'order', 'is_display_question')
    search_fields = ('lightning__title', 'title')


@admin.register(LightningAnswer)
class LightningAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct', 'is_display_answer')
    search_fields = ('question__title', 'text')
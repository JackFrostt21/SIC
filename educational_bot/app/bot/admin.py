from django.contrib import admin
from .models.bot_settings import SetsListParameter, SetsList
from .models.telegram_user import TelegramUser, UserAction, TelegramGroup

from .models.testing_module import UserTest


class SetsListParameterAdmin(admin.StackedInline):
    model = SetsListParameter
    extra = 0
    readonly_fields = ["photo_preview"]


class SetsListParameterTabularAdmin(admin.TabularInline):
    model = SetsListParameter
    extra = 0
    readonly_fields = ["photo_preview"]


@admin.register(SetsList)
class SetsListAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    inlines = [SetsListParameterAdmin, SetsListParameterTabularAdmin]


# class UserRatingInlineAdmin(admin.TabularInline):
#     model = UserRating
#     extra = 0


# class UserTestResultInlineAdmin(admin.TabularInline):
#     model = UserTestResult
#     extra = 0


# class UserAnswerInlineAdmin(admin.StackedInline):
#     model = UserAnswer
#     extra = 0


class UserTestInlineAdmin(admin.TabularInline):
    model = UserTest
    fields = ('training', 'quantity_correct', 'complete')
    readonly_fields = ('training', 'quantity_correct', 'complete')
    extra = 0


@admin.register(TelegramUser)
class TelegramUserModeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'user_name', 'state')
    list_display_links = ('user_name',)
    search_fields = ('user_id', 'user_name', 'created_at', 'updated_at', 'state')
    list_filter = ('user_name', 'created_at', 'updated_at', 'state')
    # inlines = [UserRatingInlineAdmin, UserTestResultInlineAdmin, UserAnswerInlineAdmin]
    inlines = [UserTestInlineAdmin]
    list_editable = ('state',)


@admin.register(TelegramGroup)
class TelegramGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    list_filter = ('name', 'description')
    filter_horizontal = ('users',)


@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_details', 'timestamp')
    list_display_links = ('user',)
    search_fields = ('user', 'action_details', 'timestamp')
    list_filter = ('user', 'action_details', 'timestamp')

@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'training', 'user_answer', 'complete', 'quantity_correct', 'quantity_not_correct')
    list_display_links = ('training',)
    search_fields = ('user', 'complete')
    list_filter = ('user', 'complete')



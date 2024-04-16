from django.contrib import admin
from .models.bot_settings import SetsListParameter, SetsList
from .models.telegram_user import TelegramUser


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


# Register your models here.
@admin.register(TelegramUser)
class TelegramUserModeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'user_name', 'state')
    list_display_links = ('user_name',)
    search_fields = ('user_id', 'user_name', 'created_at', 'updated_at', 'state')
    list_filter = ('user_name', 'created_at', 'updated_at', 'state')
    # inlines = [UserRatingInlineAdmin, UserTestResultInlineAdmin, UserAnswerInlineAdmin]
    list_editable = ('state',)

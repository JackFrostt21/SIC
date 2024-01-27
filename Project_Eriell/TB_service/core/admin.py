from django.contrib import admin

#импортируем класс TelegramUser
from .models import TelegramUser


"""
Декоратор @admin.register() используется для регистрации модели TelegramUser в административном интерфейсе Django.
Это позволяет Django автоматически создать интерфейс для управления объектами TelegramUser в админ-панели.
"""
@admin.register(TelegramUser)
class TelegramUserModeAdmin(admin.ModelAdmin):
    #определяет, какие поля модели будут отображаться в списке объектов на странице административного интерфейса
    list_display = ('id', 'user_id', 'user_name')

    #определяет, какие поля в списке будут являться ссылками на страницу редактирования объекта
    list_display_links = ('user_name',)
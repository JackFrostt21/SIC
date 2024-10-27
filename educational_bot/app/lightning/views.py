from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Lightning, LightningMessage, JobTitle, LightningQuestion, LightningAnswer
from app.bot.models.telegram_user import TelegramUser, TelegramGroup


from django.views.generic import View
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from app.bot.models.telegram_user import TelegramUser, TelegramGroup
from django.http import HttpResponse

from icecream import ic

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def lightnings_custom_view(request, lightning_id=None):
    lightnings = Lightning.objects.all()  # Получаем список всех молний

    lightning = None
    if 'create' in request.path:
        lightning = Lightning()  # Создаем новый пустой объект молния
    elif lightning_id:
        lightning = get_object_or_404(Lightning, id=lightning_id)

    # Получаем всех пользователей, группы и должности которые еще не привязаны к данной молнии
    if lightning and lightning.pk:
        users = TelegramUser.objects.exclude(id__in=lightning.user.all())
        groups = TelegramGroup.objects.exclude(id__in=lightning.group.all())
        job_titles = JobTitle.objects.exclude(id__in=lightning.job_titles.all())
    else:
        users = TelegramUser.objects.all()  # Если молния не выбрана, показываем всех пользователей
        groups = TelegramGroup.objects.all()  # Если молния не выбрана, показываем все группы
        job_titles = JobTitle.objects.all()  # Если молния не выбрана, показываем все должности  

    # поля для передачи в пост
    if request.method == "POST" and lightning:
        # Обновление полей объекта молнии
        lightning.title = request.POST.get('title')
        lightning.description_of_consequences = request.POST.get('description_of_consequences')
        lightning.incident_location = request.POST.get('incident_location')
        lightning.incident_coordinates = request.POST.get('incident_coordinates')
        lightning.plan_of_action = request.POST.get('plan_of_action')
        lightning.responsible_persons = request.POST.get('responsible_persons')
        min_test_percent_course = int(request.POST.get('min_test_percent_course'))
        if 0 <= min_test_percent_course <= 100:
            lightning.min_test_percent_course = min_test_percent_course
        else:
            lightning.min_test_percent_course = 0

        lightning.save()  # Сохраняем изменения в базе данных

        # Обработка удаленных элементов
        deleted_users = request.POST.get('deleted_users', '').split(',')
        deleted_groups = request.POST.get('deleted_groups', '').split(',')
        deleted_job_titles = request.POST.get('deleted_job_titles', '').split(',')

        # Удаление пользователей
        if deleted_users:
            lightning.user.remove(*[int(user_id) for user_id in deleted_users if user_id])

        # Удаление групп
        if deleted_groups:
            lightning.group.remove(*[int(group_id) for group_id in deleted_groups if group_id])

        # Удаление должностей
        if deleted_job_titles:
            lightning.job_titles.remove(*[int(job_id) for job_id in deleted_job_titles if job_id])

        # Объединяем существующих пользователей с новыми
        selected_users = request.POST.getlist('users')
        current_users = lightning.user.all()
        new_users = TelegramUser.objects.filter(id__in=selected_users)
        lightning.user.set(current_users | new_users)

        # Объединяем существующие группы с новыми
        selected_groups = request.POST.getlist('groups')
        current_groups = lightning.group.all()
        new_groups = TelegramGroup.objects.filter(id__in=selected_groups)
        lightning.group.set(current_groups | new_groups)

        # Объединяем существующие должности с новыми
        selected_job_titles = request.POST.getlist('job_titles')
        current_job_titles = lightning.job_titles.all()
        new_job_titles = JobTitle.objects.filter(id__in=selected_job_titles)
        lightning.job_titles.set(current_job_titles | new_job_titles)

        return redirect('lightning_custom', lightning_id=lightning.id)

    return render(request, 'lightning/lightning_custom.html', {
        'lightnings': lightnings,  # Все молнии
        'lightning': lightning,  # Текущая молния (или None)
        'users': users,  # Пользователи без связи с текущей молнией
        'groups': groups,  # Группы без связи с текущей молнией
        'job_titles': job_titles,  # Должности без связи с текущей молнией
    })


class LightningDeleteView(DeleteView):
    model = Lightning
    template_name = 'lightning/lightning_confirm_delete.html'
    success_url = reverse_lazy('lightning_custom')


"""для кнопки отправить сообщение"""
from app.bot.management.commands.loader import bot
from asgiref.sync import sync_to_async

async def send_lightning_view(request, lightning_id):
    lightning = await sync_to_async(get_object_or_404)(Lightning, id=lightning_id)

    # Сбор пользователей
    users = set(await sync_to_async(lambda: list(lightning.user.all()))())
    for group in await sync_to_async(lambda: list(lightning.group.all()))():
        users.update(await sync_to_async(lambda: list(group.users.all()))())
    users.update(await sync_to_async(lambda: list(TelegramUser.objects.filter(job_title__in=lightning.job_titles.all())))())

    # Убираем дубли пользователей
    users = list(set(users))


    inline_kb = InlineKeyboardMarkup()
    lightning_button = InlineKeyboardButton('Ознакомиться с молнией', callback_data=f'lightning_{lightning.id}')
    inline_kb.add(lightning_button)

    # Отправка сообщения пользователям
    for user in users:
        try:
            await bot.send_message(user.user_id, "Вам поступило новое сообщение", reply_markup=inline_kb)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user.user_id}: {e}")

    return JsonResponse({'status': 'success'})
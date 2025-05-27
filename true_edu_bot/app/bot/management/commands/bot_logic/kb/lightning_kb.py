# from aiogram.types import (
#     KeyboardButton,
#     ReplyKeyboardMarkup,
#     InlineKeyboardMarkup,
#     InlineKeyboardButton
# )
# from asgiref.sync import sync_to_async
# from datetime import timedelta
# from django.utils import timezone
# from aiogram import types
# from django.apps import apps
# from django.db.models import Q
# from app.bot.management.commands.loader import dp
# from django.db import transaction

# from app.lightning.models import LightningMessage, LightningQuestion, LightningAnswer, LightningRead, Lightning, LightningTest
# from app.bot.models import TelegramUser

# import logging

# # Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#     format="%(asctime)s [%(levelname)s] %(message)s",  # Формат логов
#     handlers=[
#         logging.StreamHandler()  # Вывод логов в консоль
#     ]
# )

# logger = logging.getLogger(__name__)

# @sync_to_async
# def get_internal_user_id(telegram_user_id):
#     try:
#         print(f"get_internal_user_id -> telegram_user_id: {telegram_user_id}")
#         user = apps.get_model('bot', 'TelegramUser').objects.get(user_id=telegram_user_id)
#         return user.id
#     except apps.get_model('bot', 'TelegramUser').DoesNotExist:
#         print(f"get_internal_user_id -> Пользователь с ID {telegram_user_id} не найден")
#         return None


# @sync_to_async
# def building_main_menu_lightning(user_id):
#     print(f"building_main_menu_lightning -> user_id: {user_id}")
#     menu_kb_lightning = ReplyKeyboardMarkup(resize_keyboard=True)
#     button_lightning  = KeyboardButton(text='Молнии')
#     button_unread = KeyboardButton(text='Не прочитанные молнии')
#     menu_kb_lightning.add(button_lightning, button_unread)
    
#     return menu_kb_lightning


# @sync_to_async
# def create_date_filter_kb(user_id):
#     print(f"create_date_filter_kb -> user_id: {user_id}")
#     kb = InlineKeyboardMarkup()
#     kb.add(
#         InlineKeyboardButton("Неделя", callback_data=f"filter_week_{user_id}"),
#         InlineKeyboardButton("Месяц", callback_data=f"filter_month_{user_id}"),
#         InlineKeyboardButton("3 Месяца", callback_data=f"filter_3-months_{user_id}")
#     )
#     return kb


# @sync_to_async
# def delete_previous_test(user_id, lightning_id):
#     """Удаляет предыдущие записи LightningTest для данного пользователя и молнии"""
#     LightningTest.objects.filter(user_id=user_id, lightning_id=lightning_id).delete()


# @dp.callback_query_handler(lambda c: c.data.startswith('filter_'))
# async def filter_lightning_by_date(callback_query: types.CallbackQuery):
#     data = callback_query.data.split('_')
#     period = data[1]
#     user_id = int(data[2])

#     # Выводим данные для отладки
#     print(f"filter_lightning_by_date -> period: {period}, user_id: {user_id}")

#     # Определяем фильтр по времени
#     current_date = timezone.now()
#     if period == 'week':
#         filter_date = current_date - timedelta(days=7)
#     elif period == 'month':
#         filter_date = current_date - timedelta(days=31)
#     elif period == '3-months':
#         filter_date = current_date - timedelta(days=90)

#     print(f"filter_lightning_by_date -> filter_date: {filter_date}")

#     # Генерация клавиатуры с отфильтрованными молниями
#     kb = await lightning_menu_kb_generator(user_id, filter_date)

#     # Отправляем отфильтрованные молнии пользователю
#     if kb:
#         print(f"filter_lightning_by_date -> отправка списка молний для user_id: {user_id}")
#         await callback_query.message.edit_text("Выберите молнию:", reply_markup=kb)
#         logger.info(f"Детали callback_query.message: {callback_query.message}")
#     else:
#         print(f"filter_lightning_by_date -> молнии отсутствуют для user_id: {user_id}")
#         await callback_query.message.edit_text("Нет доступных молний за выбранный период.")
#         logger.info(f"Детали callback_query.message: {callback_query.message}")


# @sync_to_async
# def mark_lightning_as_read(user_id, lightning_id):
#     """Функция для записи в модель LightningRead при нажатии на 'Ознакомился'"""
#     # Получаем пользователя и молнию
#     user = TelegramUser.objects.get(id=user_id)
#     lightning = Lightning.objects.get(id=lightning_id)
#     print(f"mark_lightning_as_read -> user: {user_id}")
#     print(f"mark_lightning_as_read -> lightning: {lightning_id}")
#     # Проверяем, есть ли уже запись о прочтении
#     # Создаем или обновляем запись
#     LightningRead.objects.update_or_create(
#         user=user,
#         lightning=lightning,
#         defaults={'is_read': True}
#     )


# @sync_to_async
# def lightning_menu_kb_generator(user_id, filter_date):
#     try:
#         print(f"lightning_menu_kb_generator -> user_id: {user_id}, filter_date: {filter_date}")
        
#         # Получаем экземпляр пользователя
#         user_instance = apps.get_model('bot', 'TelegramUser').objects.get(id=user_id)
#         print(f"lightning_menu_kb_generator -> Пользователь найден: {user_instance}")
        
#         # Получаем группы, в которых состоит пользователь
#         user_groups = apps.get_model('bot', 'TelegramGroup').objects.filter(users__id=user_id)
#         print(f"lightning_menu_kb_generator -> Группы пользователя: {user_groups}")

#         # Получаем все объекты Lightning, которые актуальны для пользователя и созданы после filter_date
#         lightnings = apps.get_model('lightning', 'Lightning').objects.filter(
#             (Q(user__id=user_id) | 
#             Q(group__in=user_groups) | 
#             Q(job_titles=user_instance.job_title)) & 
#             Q(created_at__gte=filter_date)  # Фильтрация по дате
#         ).distinct()

#         print(f"lightning_menu_kb_generator -> Найдено молний: {len(lightnings)}")

#         # Создаем инлайн-клавиатуру для найденных объектов Lightning
#         menu_kb_lightning = InlineKeyboardMarkup()

#         for lightning in lightnings:
#             button = InlineKeyboardButton(
#                 text=lightning.title,
#                 callback_data=f"lightning_{lightning.id}"
#             )
#             menu_kb_lightning.add(button)

#         # Если молний нет
#         if not menu_kb_lightning.inline_keyboard:
#             print("lightning_menu_kb_generator -> Нет доступных молний")
#             button = InlineKeyboardButton(text="Нет доступных молний", callback_data="no_lightnings")
#             menu_kb_lightning.add(button)

#         return menu_kb_lightning

#     except Exception as e:
#         print(f"Error in lightning_menu_kb_generator: {e}")
#         return None


# @dp.message_handler(lambda message: message.text == "Не прочитанные молнии")
# async def send_unread_lightnings(message: types.Message):
#     # Получаем Telegram ID пользователя
#     telegram_user_id = message.from_user.id

#     # Находим внутренний ID пользователя
#     user_id = await get_internal_user_id(telegram_user_id)
#     if not user_id:
#         await message.answer("Ошибка: пользователь не найден.")
#         return

#     # Получаем список непрочитанных молний
#     async def get_unread_lightnings(user_id):
#         return await sync_to_async(lambda: list(Lightning.objects.filter(
#             id__in=LightningRead.objects.filter(user_id=user_id, is_read=False).values_list('lightning_id', flat=True)
#         ).order_by('-created_at')))()

#     unread_lightnings = await get_unread_lightnings(user_id)

#     if not unread_lightnings:
#         await message.answer("У вас нет непрочитанных молний.")
#         return

#     # Генерация инлайн-клавиатуры с непрочитанными молниями
#     inline_kb = InlineKeyboardMarkup()
#     for lightning in unread_lightnings:
#         button = InlineKeyboardButton(
#             text=lightning.title,
#             callback_data=f'lightning_{lightning.id}'
#         )
#         inline_kb.add(button)

#     # Отправляем сообщение с инлайн-кнопками
#     await message.answer(
#         "Список непрочитанных молний. Нажмите на молнию, чтобы ознакомиться:",
#         reply_markup=inline_kb
#     )


# @sync_to_async
# def get_lightning_messages(lightning_id):
#     print(f"get_lightning_messages -> lightning_id: {lightning_id}")
#     return list(LightningMessage.objects.filter(lightning_id=lightning_id).order_by('order', 'id'))


# @sync_to_async
# def get_lightning_questions(lightning_id):
#     print(f"get_lightning_questions -> lightning_id: {lightning_id}")
#     return list(LightningQuestion.objects.filter(lightning_id=lightning_id, is_display_question=True).order_by('order', 'id'))

# @sync_to_async
# def get_lightning_answers(question_id):
#     print(f"get_lightning_answers -> question_id: {question_id}")
#     return list(LightningAnswer.objects.filter(question_id=question_id, is_display_answer=True).order_by('number', 'id'))


# @dp.callback_query_handler(lambda c: c.data.startswith('lightning_'))
# async def list_lightning_messages(callback_query: types.CallbackQuery):
#     data = callback_query.data.split('_')
#     lightning_id = int(data[1])  # Забираем ID молнии
#     telegram_user_id = callback_query.from_user.id  # Получаем Telegram ID пользователя

#     # Ищем внутренний ID пользователя по Telegram ID
#     user_id = await get_internal_user_id(telegram_user_id)

#     if not user_id:
#         await callback_query.message.answer("Ошибка: пользователь не найден.")
#         logger.info(f"Детали callback_query.message: {callback_query.message}")
#         print(f"list_lightning_messages -> Ошибка: пользователь с telegram_user_id {telegram_user_id} не найден.")
#         await callback_query.answer()
#         return

#     print(f"list_lightning_messages -> lightning_id: {lightning_id}, internal_user_id: {user_id}")

#     # Получаем все лайтнинг мэсседж по ID молнии
#     messages = await get_lightning_messages(lightning_id)

#     if not messages:
#         await callback_query.message.answer('Для молнии нет сообщений')
#         logger.info(f"Детали callback_query.message: {callback_query.message}")
#         await callback_query.answer()
#         return
    
#     # Отправляем первое сообщение (по order)
#     await show_lightning_message_kb(callback_query, messages, 0, user_id)
#     await callback_query.answer()


# async def show_lightning_message_kb(callback_query, messages, message_index, user_id):
#     logger.info(f"Показ сообщения -> Индекс: {message_index}, Пользователь ID: {user_id}")
#     print(f"show_lightning_message_kb -> message_index: {message_index}, user_id: {user_id}")

#     message = messages[message_index]
#     logger.info(f"Содержимое сообщения: {message.content}")
#     logger.info(f"Флаг send_text: {message.send_text}")
#     logger.info(f"Файл сообщения: {message.file_lightning}")
#     logger.info(f"Изображение сообщения: {message.image_lightning}")


#     # Создаем инлайн-клавиатуру
#     kb = InlineKeyboardMarkup()

#     # Добавляем кнопку WebApp для открытия файла, если send_file=True и файл присутствует
#     if message.send_file and message.file_lightning:
#         file_url = f"https://educationalbot.engsdrilling.ru/lightning/pdf/{message.id}/"
#         # file_url = f"https://127.0.0.1:8000/lightning/pdf/{message.id}/"
#         kb.add(InlineKeyboardButton("Открыть файл", web_app=types.WebAppInfo(url=file_url)))

#     # Проверка, есть ли следующее сообщение
#     if message_index + 1 < len(messages):
#         next_buttons_text = message.button_text if message.button_text else 'Далее'
#         kb.add(InlineKeyboardButton(next_buttons_text, callback_data=f'lightning-message_{message.id}_{message_index + 1}'))
#     else:
#         # Проверяем количество вопросов для текущей молнии
#         lightning_id = await sync_to_async(lambda: message.lightning.id)()
#         questions = await get_lightning_questions(lightning_id)
        
#         if len(questions) > 0:
#             # Если есть вопросы, показываем кнопку "Начать тестирование"
#             kb.add(InlineKeyboardButton("Начать тестирование", callback_data=f"start_test_{lightning_id}"))
#         else:
#             # Если вопросов нет, показываем кнопку "Ознакомился"
#             kb.add(InlineKeyboardButton("Ознакомился", callback_data=f"close_lightning_{lightning_id}"))

#     # Проверяем, есть ли изображение для текущего сообщения
#     if message.image_lightning:
#         image_path = f"media/{message.image_lightning}"
#         print(f"show_lightning_message_kb -> Путь к изображению: {image_path}")

#         try:
#             with open(image_path, "rb") as file:
#                 # Отправляем новое сообщение с изображением
#                 if message.send_text:    
#                     await callback_query.message.answer_photo(photo=file, caption=message.content, reply_markup=kb)
#                     logger.info(f"Детали callback_query.message: {callback_query.message}")
#                 else:
#                     await callback_query.message.answer_photo(photo=file, reply_markup=kb)
#                     logger.info(f"Детали callback_query.message: {callback_query.message}")    
#         except FileNotFoundError:
#             print(f"show_lightning_message_kb -> Ошибка: файл изображения не найден по пути {image_path}")
#             if message.send_text:
#                 await callback_query.message.edit_text(text=message.content, reply_markup=kb)
#                 logger.info(f"Детали callback_query.message: {callback_query.message}")
#             else:
#                 await callback_query.message.edit_reply_markup(reply_markup=kb)
#                 logger.info(f"Детали callback_query.message: {callback_query.message}")
#     else:
#         if message.send_text:
#             await callback_query.message.edit_text(text=message.content, reply_markup=kb)
#             logger.info(f"Детали callback_query.message: {callback_query.message}")
#         else:
#             await callback_query.message.edit_reply_markup(reply_markup=kb)
#             logger.info(f"Детали callback_query.message: {callback_query.message}")


# @dp.callback_query_handler(lambda c: c.data.startswith('lightning-message_'))
# async def content_lightning_messages(callback_query: types.CallbackQuery):
#     data = callback_query.data.split('_')
#     lightning_message_id = int(data[1])  # Извлекаем ID сообщения
#     message_index = int(data[2])  # Извлекаем индекс сообщения
#     user_id = callback_query.from_user.id  # Получаем user_id
#     print(f"content_lightning_messages -> lightning_message_id: {lightning_message_id}, message_index: {message_index}, telegram_user_id: {user_id}")

#     lightning_message = await sync_to_async(LightningMessage.objects.get)(id=lightning_message_id)
#     # Получаем все сообщения
#     lightning_id = await sync_to_async(lambda: lightning_message.lightning.id)()
#     messages = await get_lightning_messages(lightning_id)

#     # Показываем следующее сообщение
#     await show_lightning_message_kb(callback_query, messages, message_index, user_id)
#     await callback_query.answer()


# @dp.callback_query_handler(lambda c: c.data.startswith("back-to-lightning-list_"))
# async def back_to_lightning_list(callback_query: types.CallbackQuery):
#     data = callback_query.data.split('_')
#     user_id = int(data[1])

#     # Получаем клавиатуру для выбора молний
#     kb = await create_date_filter_kb(user_id)

#     # Отправляем новое сообщение с клавиатурой
#     await callback_query.message.answer("Выберите период:", reply_markup=kb)
#     logger.info(f"Детали callback_query.message: {callback_query.message}")

#     # Закрываем запрос пользователя
#     await callback_query.answer()


# #Обработка кнопки ознакомился
# @dp.callback_query_handler(lambda c: c.data.startswith("close_lightning_"))
# async def close_lightning_message(callback_query: types.CallbackQuery):
#     print(f"close_lightning_message -> callback_query.from_user.id: {callback_query.from_user.id}")
    
#     # Получаем ID молнии из callback_data
#     lightning_id = int(callback_query.data.split('_')[2])
    
#     # Получаем внутренний ID пользователя
#     telegram_user_id = callback_query.from_user.id
#     user_id = await get_internal_user_id(telegram_user_id)
#     print(f"close_lightning_message -> lightning_id: {lightning_id}, telegram_user_id: {telegram_user_id}, user_id: {user_id}")
#     if not user_id:
#         await callback_query.message.answer("Ошибка: пользователь не найден.")
#         logger.info(f"Детали callback_query.message: {callback_query.message}")
#         await callback_query.answer()
#         return

#     # Отмечаем молнию как прочитанную
#     record_created = await mark_lightning_as_read(user_id, lightning_id)

#     # Проверяем наличие других непрочитанных молний
#     unread_lightnings = await fetch_unread_lightnings(user_id)
    
#     if unread_lightnings:
#         # Генерация инлайн-клавиатуры с непрочитанными молниями
#         inline_kb = InlineKeyboardMarkup()
#         for lightning in unread_lightnings:
#             button = InlineKeyboardButton(
#                 text=lightning.title,
#                 callback_data=f'lightning_{lightning.id}'
#             )
#             inline_kb.add(button)
        
#         # Отправляем сообщение с инлайн-кнопками
#         await callback_query.message.answer(
#             "У вас есть другие непрочитанные молнии. Ознакомьтесь, нажав на соответствующую кнопку:",
#             reply_markup=inline_kb
#         )
#     else:
#         # Если непрочитанных молний нет
#         await callback_query.message.answer("У вас нет новых молний.")
    
#     logger.info(f"Детали callback_query.message: {callback_query.message}")
#     await callback_query.answer()


# @sync_to_async
# def fetch_unread_lightnings(user_id):
#     """Возвращает список непрочитанных молний для пользователя"""
#     return list(Lightning.objects.filter(
#         id__in=LightningRead.objects.filter(user_id=user_id, is_read=False).values_list('lightning_id', flat=True)
#     ).order_by('-created_at'))


# """Тестирование"""

# # Символы для отображения выбранных и невыбранных ответов
# unselected_symbol = "⚪"  # Не выбран
# selected_symbol = "🟢"    # Выбран

# # Старт теста
# @dp.callback_query_handler(lambda c: c.data.startswith('start_test_'))
# async def lightning_start_test(callback_query: types.CallbackQuery):
#     # Извлекаем lightning_id из callback_data
#     lightning_id = int(callback_query.data.split('_')[2])

#     print(f"lightning_start_test -> callback_query.from_user.id: {callback_query.from_user.id}, lightning_id: {lightning_id}")

#     # Получаем внутренний ID пользователя
#     telegram_user_id = callback_query.from_user.id
#     user_id = await get_internal_user_id(telegram_user_id)

#     if not user_id:
#         await callback_query.message.answer("Ошибка: пользователь не найден.")
#         logger.info(f"Детали callback_query.message: {callback_query.message}")
#         await callback_query.answer()
#         return

#     # Удаляем предыдущую запись теста, если она существует
#     await delete_previous_test(user_id, lightning_id)

#     # Отмечаем молнию как прочитанную перед тестированием
#     await mark_lightning_as_read(user_id, lightning_id)

#     # Получаем список вопросов для данной молнии
#     questions = await get_lightning_questions(lightning_id)

#     if not questions:
#         await callback_query.message.answer("К сожалению, для этой молнии нет доступных вопросов.")
#         logger.info(f"Детали callback_query.message: {callback_query.message}")
#     else:
#         # Начинаем с первого вопроса
#         first_question_index = 0
#         # Обнуляем выбранные ответы
#         selected_answers = {}
#         # Начинаем показ вопросов
#         await show_question(callback_query.message, questions, first_question_index, selected_answers, lightning_id)
#         logger.info(f"Детали callback_query.message: {callback_query.message}")

#     # Отвечаем на callback, чтобы закрыть спиннер
#     await callback_query.answer()


# async def show_question(message, questions, question_index, selected_answers, lightning_id):
#     """Функция для отображения конкретного вопроса с вариантами ответов"""

#     # Проверяем, что индекс вопроса в пределах списка
#     if question_index >= len(questions):
#         print(f"Ошибка: Вопрос с индексом {question_index} выходит за пределы списка. Всего вопросов: {len(questions)}")
#         return

#     question = questions[question_index]

#     # Получаем общее количество вопросов
#     total_questions = len(questions)

#     # Формируем текст вопроса
#     question_text = f"<b>Тестирование</b>\n\n"
#     question_text += f"Вопрос ({question_index + 1} из {total_questions}):\n"
#     question_text += f"<i>{question.title}</i>\n\n"

#     # Получаем все ответы для данного вопроса
#     answers = await get_lightning_answers(question.id)

#     if not answers:
#         print(f"Ошибка: Нет ответов для вопроса {question.id}")

#     # Формируем текст для отображения списка ответов под вопросом
#     answers_text = ""
#     for answer in answers:
#         label = answer.number  # Используем поле 'number' из модели
#         answers_text += f"<b>{label})</b> {answer.text}\n\n"

#     # Добавляем предупреждение для множественного выбора
#     if question.is_multiple_choice:
#         answers_text += "Выберите несколько правильных ответов\n"
#     else:
#         answers_text += "Выберите один правильный ответ\n"

#     full_question_text = f"{question_text}{answers_text}"

#     # Создаем инлайн-клавиатуру с вариантами ответов
#     kb = InlineKeyboardMarkup()

#     for answer in answers:
#         label = answer.number  # Используем поле 'number' из модели
#         # Проверяем, был ли выбран данный ответ
#         answer_id_str = str(answer.id)
#         if question.id in selected_answers and answer_id_str in selected_answers[question.id]:
#             symbol = selected_symbol
#         else:
#             symbol = unselected_symbol

#         button_text = f"{symbol} {label}"
#         kb.add(InlineKeyboardButton(
#             text=button_text,
#             callback_data=f"answer_{lightning_id}_{question.id}_{answer.id}_{question_index}"
#         ))

#     # Добавляем кнопки навигации
#     nav_buttons = []

#     # Кнопка "Назад" (если это не первый вопрос)
#     if question_index > 0:
#         nav_buttons.append(
#             InlineKeyboardButton(
#                 text="Назад",
#                 callback_data=f"prev_question_{question_index - 1}"
#             )
#         )

#     # Кнопка "Вперед" (если это не последний вопрос и выбран хотя бы один ответ)
#     if question_index < total_questions - 1 and selected_answers.get(question.id):
#         nav_buttons.append(
#             InlineKeyboardButton(
#                 text="Вперед",
#                 callback_data=f"next-question_{question_index + 1}"
#             )
#         )

#     # Добавляем кнопки навигации в клавиатуру
#     if nav_buttons:
#         kb.row(*nav_buttons)

#     # Кнопка "Завершить тестирование"
#     kb.add(InlineKeyboardButton(
#         text="Завершить тестирование",
#         callback_data="finish_test"
#     ))

#     # Отправляем или редактируем сообщение с вопросом
#     try:
#         if message.photo:
#             print("show_question -> Сообщение содержит изображение, удаляем сообщение и отправляем новое.")
#             await message.delete()
#             await message.answer(full_question_text, reply_markup=kb, parse_mode='HTML')
#         else:
#             await message.edit_text(full_question_text, reply_markup=kb, parse_mode='HTML')
#     except Exception as e:
#         print(f"Ошибка при редактировании сообщения: {e}")
#         await message.answer(full_question_text, reply_markup=kb, parse_mode='HTML')


# # Обработчик выбора ответа
# @dp.callback_query_handler(lambda c: c.data.startswith('answer_'))
# async def handle_answer(callback_query: types.CallbackQuery):
#     # Извлекаем данные из callback_data
#     _, lightning_id, question_id, answer_id, question_index = callback_query.data.split('_')
#     lightning_id = int(lightning_id)
#     question_id = int(question_id)
#     answer_id = int(answer_id)
#     question_index = int(question_index)

#     print(f"handle_answer -> lightning_id: {lightning_id}, question_id: {question_id}, answer_id: {answer_id}, question_index: {question_index}")

#     # Получаем внутренний ID пользователя
#     telegram_user_id = callback_query.from_user.id
#     user_id = await get_internal_user_id(telegram_user_id)

#     # Получаем информацию о вопросе
#     question = await sync_to_async(LightningQuestion.objects.get)(id=question_id)
#     is_multiple_choice = question.is_multiple_choice

#     # Получаем уже выбранные ответы для этого вопроса
#     selected_answers = await get_selected_answers(user_id, lightning_id, question_id)

#     answer_id_str = str(answer_id)

#     if is_multiple_choice:
#         # Для множественного выбора добавляем или удаляем ответ
#         if answer_id_str in selected_answers:
#             selected_answers.remove(answer_id_str)
#         else:
#             selected_answers.append(answer_id_str)
#     else:
#         # Для одиночного выбора заменяем ответ
#         selected_answers = [answer_id_str]

#     # Сохраняем ответ пользователя
#     await save_user_answer(user_id, lightning_id, question_id, selected_answers, is_multiple_choice)

#     # Получаем список вопросов
#     questions = await get_lightning_questions(lightning_id)

#     # Обновляем выбранные ответы
#     all_selected_answers = await get_all_selected_answers(user_id, lightning_id)

#     # Переходим к текущему вопросу с обновленными выбранными ответами
#     await show_question(callback_query.message, questions, question_index, all_selected_answers, lightning_id)

#     # Отвечаем на callback
#     await callback_query.answer()


# # Обработчик кнопки "Вперед"
# @dp.callback_query_handler(lambda c: c.data.startswith('next-question_'))
# async def next_question(callback_query: types.CallbackQuery):
#     _, next_question_index = callback_query.data.split('_')
#     next_question_index = int(next_question_index)

#     print(f"next_question -> next_question_index: {next_question_index}")

#     # Получаем lightning_id из сообщения
#     message = callback_query.message
#     # Извлекаем lightning_id из callback_data кнопки ответа
#     try:
#         lightning_id = int(message.reply_markup.inline_keyboard[0][0].callback_data.split('_')[1])
#     except Exception as e:
#         print(f"Ошибка при извлечении lightning_id: {e}")
#         await callback_query.answer("Ошибка при переходе к следующему вопросу.")
#         return

#     # Получаем список вопросов
#     questions = await get_lightning_questions(lightning_id)

#     # Получаем внутренний ID пользователя
#     telegram_user_id = callback_query.from_user.id
#     user_id = await get_internal_user_id(telegram_user_id)

#     # Получаем все выбранные ответы
#     selected_answers = await get_all_selected_answers(user_id, lightning_id)

#     # Переходим к следующему вопросу
#     await show_question(callback_query.message, questions, next_question_index, selected_answers, lightning_id)
#     logger.info(f"Детали callback_query.message: {callback_query.message}")

#     # Отвечаем на callback
#     await callback_query.answer()


# # Обработчик кнопки "Назад"
# @dp.callback_query_handler(lambda c: c.data.startswith('prev_question_'))
# async def prev_question(callback_query: types.CallbackQuery):
#     _, prev_question_index = callback_query.data.split('_')
#     prev_question_index = int(prev_question_index)

#     print(f"prev_question -> prev_question_index: {prev_question_index}")

#     # Получаем lightning_id из сообщения
#     message = callback_query.message
#     # Извлекаем lightning_id из callback_data кнопки ответа
#     try:
#         lightning_id = int(message.reply_markup.inline_keyboard[0][0].callback_data.split('_')[1])
#     except Exception as e:
#         print(f"Ошибка при извлечении lightning_id: {e}")
#         await callback_query.answer("Ошибка при переходе к предыдущему вопросу.")
#         return

#     # Получаем список вопросов
#     questions = await get_lightning_questions(lightning_id)

#     # Получаем внутренний ID пользователя
#     telegram_user_id = callback_query.from_user.id
#     user_id = await get_internal_user_id(telegram_user_id)

#     # Получаем все выбранные ответы
#     selected_answers = await get_all_selected_answers(user_id, lightning_id)

#     # Переходим к предыдущему вопросу
#     await show_question(callback_query.message, questions, prev_question_index, selected_answers, lightning_id)

#     # Отвечаем на callback
#     await callback_query.answer()


# # Обработчик завершения теста
# @dp.callback_query_handler(lambda c: c.data == 'finish_test')
# async def finish_test(callback_query: types.CallbackQuery):
#     telegram_user_id = callback_query.from_user.id
#     user_id = await get_internal_user_id(telegram_user_id)

#     # Извлекаем lightning_id из сообщения
#     message = callback_query.message
#     try:
#         lightning_id = int(message.reply_markup.inline_keyboard[0][0].callback_data.split('_')[1])
#     except Exception as e:
#         print(f"Ошибка при извлечении lightning_id: {e}")
#         await callback_query.answer("Ошибка при завершении теста.")
#         return

#     # Подсчитываем результаты
#     result_message = await counting_correct_answers(user_id, lightning_id)

#     # Отправляем результат пользователю
#     await callback_query.message.answer(result_message, parse_mode='HTML')

#     # Удаляем сообщение с последним вопросом
#     await callback_query.message.delete()

#     # Проверяем наличие других непрочитанных молний
#     unread_lightnings = await fetch_unread_lightnings(user_id)

#     if unread_lightnings:
#         # Генерация инлайн-клавиатуры с непрочитанными молниями
#         inline_kb = InlineKeyboardMarkup()
#         for lightning in unread_lightnings:
#             button = InlineKeyboardButton(
#                 text=lightning.title,
#                 callback_data=f'lightning_{lightning.id}'
#             )
#             inline_kb.add(button)

#                     # Отправляем сообщение с инлайн-кнопками
#         await callback_query.message.answer(
#             "У вас есть другие непрочитанные молнии. Ознакомьтесь, нажав на соответствующую кнопку:",
#             reply_markup=inline_kb
#         )
#     else:
#         # Если непрочитанных молний нет
#         await callback_query.message.answer("У вас нет новых молний.")

#     # Отвечаем на callback
#     await callback_query.answer()


# @sync_to_async
# def save_user_answer(user_id, lightning_id, question_id, selected_answers, is_multiple_choice):
#     """Сохраняет ответ пользователя и обновляет запись теста"""

#     from app.lightning.models import LightningTest

#     # Получаем или создаем запись теста для пользователя и молнии
#     lightning_test, _ = LightningTest.objects.get_or_create(
#         user_id=user_id,
#         lightning_id=lightning_id,
#         defaults={'complete': False, 'user_answer': {'results': []}}
#     )

#     user_answers = lightning_test.user_answer.get("results", [])

#     # Проверяем, есть ли уже ответ на этот вопрос
#     existing_result = next((result for result in user_answers if result["question_id"] == question_id), None)

#     if existing_result:
#         existing_result["answer"] = selected_answers
#     else:
#         # Добавляем новый результат
#         new_result = {"question_id": question_id, "answer": selected_answers}
#         user_answers.append(new_result)

#     # Обновляем JSON поле с ответами
#     lightning_test.user_answer = {"results": user_answers}

#     # Сохранение изменений
#     lightning_test.save()


# @sync_to_async
# def get_selected_answers(user_id, lightning_id, question_id):
#     """Получает выбранные ответы пользователя для конкретного вопроса"""
#     from app.lightning.models import LightningTest

#     try:
#         lightning_test = LightningTest.objects.get(user_id=user_id, lightning_id=lightning_id)
#         user_answers = lightning_test.user_answer.get("results", [])

#         existing_result = next((result for result in user_answers if result["question_id"] == question_id), None)

#         if existing_result:
#             return existing_result.get("answer", [])
#         else:
#             return []
#     except LightningTest.DoesNotExist:
#         return []


# @sync_to_async
# def get_all_selected_answers(user_id, lightning_id):
#     """Получает все выбранные ответы пользователя"""
#     from app.lightning.models import LightningTest

#     selected_answers = {}
#     try:
#         lightning_test = LightningTest.objects.get(user_id=user_id, lightning_id=lightning_id)
#         user_answers = lightning_test.user_answer.get("results", [])

#         for result in user_answers:
#             question_id = result["question_id"]
#             answers = result.get("answer", [])
#             selected_answers[question_id] = answers

#         return selected_answers
#     except LightningTest.DoesNotExist:
#         return {}


# @sync_to_async
# def counting_correct_answers(user_id, lightning_id):
#     """Подсчитывает результаты теста и возвращает сообщение с результатом"""
#     from app.lightning.models import LightningTest, LightningQuestion, LightningAnswer, Lightning

#     lightning_test = LightningTest.objects.get(user_id=user_id, lightning_id=lightning_id)
#     results = lightning_test.user_answer.get("results", [])

#     quantity_correct = 0
#     quantity_not_correct = 0

#     for result in results:
#         question_id = result["question_id"]
#         selected_answers = result.get("answer", [])

#         # Получаем правильные ответы для вопроса
#         correct_answers = list(LightningAnswer.objects.filter(
#             question_id=question_id,
#             is_correct=True
#         ).values_list('id', flat=True))
#         correct_answers = list(map(str, correct_answers))

#         if set(selected_answers) == set(correct_answers):
#             quantity_correct += 1
#         else:
#             quantity_not_correct += 1

#     total_questions = quantity_correct + quantity_not_correct
#     correct_percent = (100 * quantity_correct) // total_questions if total_questions else 0
#     incorrect_percent = 100 - correct_percent

#     # Получаем минимальный процент для сдачи
#     lightning = Lightning.objects.get(id=lightning_id)
#     min_test_percent = lightning.min_test_percent_course

#     # Определяем успешность прохождения теста
#     is_complete = correct_percent >= min_test_percent
#     lightning_test.complete = is_complete
#     lightning_test.quantity_correct = correct_percent
#     lightning_test.quantity_not_correct = incorrect_percent
#     lightning_test.save()

#     # Формируем сообщение с результатом
#     lightning_title = lightning.title
#     result_message = (
#         f"Ваш результат по тесту <b>{lightning_title}</b>\n\n"
#         f"<b>Верных ответов:</b> {correct_percent}%\n"
#         f"<b>Неверных ответов:</b> {incorrect_percent}%\n\n"
#     )
#     if is_complete:
#         result_message += "Поздравляем, вы успешно сдали тест!"
#     else:
#         result_message += "К сожалению, вы не сдали тест."

#     return result_message
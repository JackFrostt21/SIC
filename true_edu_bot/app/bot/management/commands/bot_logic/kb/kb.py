from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from asgiref.sync import sync_to_async
from django.apps import apps
from django.db.models import Q
from django.utils.safestring import mark_safe
import datetime


from app.bot.models import UserTest
from app.bot.management.commands.bot_logic.functions import paginate_text, remove_unsupported_html_tags
from app.bot.models.telegram_user import UserRead
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.loader import dp
from app.bot.management.commands.bot_logic.callbackfactory import topic_menu, begin_test, content_selection, pdf_callback, audio_callback, video_callback

i18n = setup_middleware(dp)
_ = i18n.gettext


@sync_to_async
def course_menu_kb_generator(user):
    try:
        # Получаем экземпляр пользователя
        user_instance = apps.get_model('bot', 'TelegramUser').objects.get(id=user.id)

        # Получаем группы, в которых состоит пользователь
        user_groups = apps.get_model('bot', 'TelegramGroup').objects.filter(users=user_instance)

        # Фильтруем курсы по актуальности и принадлежности пользователю или его группе
        menu_list = apps.get_model('educational_module', 'TrainingCourse').objects.filter(
            is_actual=True
        ).filter(
            Q(user=user_instance) | Q(group__in=user_groups)
        ).distinct()

        kb = types.InlineKeyboardMarkup(inline_keyboard=[])
        today = datetime.date.today()

        for course in menu_list:
            # Проверяем, есть ли дедлайн для курса, актуальный для данного пользователя/групп,
            # и если дедлайн наступил, пропускаем этот курс
            course_deadline_expired = course.deadlines.filter(
                deadline_date__lte=today
            ).filter(
                Q(deadline_telegramusers=user_instance) | Q(deadline_groups__in=user_groups)
            ).exists()

            if course_deadline_expired:
                continue  # Пропускаем курс, если дедлайн уже наступил

            # Проверяем, завершен ли тест по этому курсу
            user_test_exists = UserTest.objects.filter(
                user_id=user_instance.id,  # Используем внутренний идентификатор пользователя
                training_id=course.id,  # Используем идентификатор курса
                complete=True
            ).exists()

            user_test_percent = UserTest.objects.filter(
                user_id=user_instance.id, # Используем внутренний идентификатор пользователя
                training_id=course.id,  # Используем идентификатор курс
            ).first()
            
            if user_test_percent:
                quantity_correct = user_test_percent.quantity_correct
            else:
                quantity_correct = None

            # Проверяем, есть ли хоть какие-то записи в UserTest по этому курсу
            user_test_record_exists = UserTest.objects.filter(
                user_id=user_instance.id,  # Используем внутренний идентификатор пользователя
                training_id=course.id  # Используем идентификатор курса
            ).exists()

            if user_test_exists:
                # course_title = f'✅{course.title} ({quantity_correct}%)'
                course_title = f'✔️ {course.title} ({quantity_correct}%)'
            elif user_test_record_exists:
                course_title = f'❌{course.title} ({quantity_correct}%)'
            else:
                course_title = f'{course.title}'

            kb.add(types.InlineKeyboardButton(text=course_title,
                                              callback_data=topic_menu.new(
                                                  info='topic',
                                                  course_id=course.id,
                                                  topic_id='-',
                                                  subtopic_id='-',
                                                  page=0)))

        return kb
    except Exception as e:
        print(f"Error in course_menu_kb_generator: {e}")
        return None
    

@sync_to_async
def topic_menu_kb_generator(course_id, internal_user_id, page=0):
    try:
        kb = types.InlineKeyboardMarkup(row_width=2)
        course = apps.get_model('educational_module.TrainingCourse').objects.get(id=course_id)

        content = f'Курс: <b>{course.title}</b>\nСписок разделов:\n<i>{course.description}</i>'
        content_pages = paginate_text(content)

        menu_list = apps.get_model('educational_module.CourseTopic').objects.filter(is_actual=True, training_course=course_id)

        # Создаем список для кнопок
        buttons = []
        long_buttons = []

        for topic in menu_list:
            # Проверка, прочитал ли пользователь эту тему
            user_read_exists = UserRead.objects.filter(user_id=internal_user_id, course_id=course_id, topic_id=topic.id, is_read=True).exists()

            # Добавляем галочку, если тема прочитана
            topic_name = f'✔️{topic.title}' if user_read_exists else f'{topic.title}'
            button = types.InlineKeyboardButton(text=topic_name,
                                                callback_data=content_selection.new(
                                                    action='select_content',
                                                    course_id=course_id,
                                                    topic_id=topic.id,
                                                    page=0))
            
            # Проверяем длину названия топика
            if len(topic_name) > 14:
                long_buttons.append(button)
            else:
                buttons.append(button)

        # Добавляем длинные кнопки (более 14 символов) в отдельные строки
        for long_button in long_buttons:
            kb.add(long_button)

        # Добавляем остальные кнопки парами
        for i in range(0, len(buttons), 2):
            kb.row(*buttons[i:i+2])

        user_test_exists = UserTest.objects.filter(
            user_id=internal_user_id,
            training_id=course_id,
            complete=True
        ).exists()

        user_test_percent = UserTest.objects.filter(
            user_id=internal_user_id,
            training_id=course_id,
        ).first()
        
        if user_test_percent:
            quantity_correct = user_test_percent.quantity_correct
        else:
            quantity_correct = None

        user_test_record_exists = UserTest.objects.filter(
            user_id=internal_user_id,
            training_id=course_id,
        ).exists()

        if user_test_exists:
            go_test_text = f'✔️ Тест ({quantity_correct}%)'
        elif user_test_record_exists:
            go_test_text = f'❌ Тест ({quantity_correct}%)'
        else:
            go_test_text = f'Тест'

        kb.add(types.InlineKeyboardButton(text=go_test_text,
                                          callback_data=begin_test.new(
                                              info="on_test",
                                              course_id=course_id,
                                              question_id=0,
                                              next_question=0,
                                              answer_id='-')))
        kb.add(types.InlineKeyboardButton(text=_('← к списку курсов'),
                                          callback_data=topic_menu.new(
                                              info='course',
                                              course_id=course_id,
                                              topic_id='-',
                                              subtopic_id='-',
                                              page=0)))

        return kb, content_pages[page], course.image_course
    except Exception as e:
        print(f"Error in topic_menu_kb_generator: {e}")
        return None, None, None
    

@sync_to_async
def subtopic_menu_kb_generator(course_id, topic_id, internal_user_id, page=0):
    kb = types.InlineKeyboardMarkup(row_width=3) #Тут добавил ,продолжить!!!
    topic = apps.get_model('educational_module.CourseTopic').objects.get(id=topic_id)
    content = f'Раздел: <b>{topic.title}</b>\n<i>{topic.description}</i>'
    content_pages = paginate_text(content)
    # Очистка только содержимого страниц
    content_pages = [remove_unsupported_html_tags(page) for page in content_pages]

    user_read_exists = UserRead.objects.filter(user_id=internal_user_id, course_id=course_id, topic_id=topic_id, is_read=True).exists()
    # checkmark = " ✔️" if user_read_exists else ""
    checkmark = "" if user_read_exists else ""

    buttons = []

    if topic.main_text_readuser:
        buttons.append(types.InlineKeyboardButton(text=f"{checkmark}Текст",
                                          callback_data=content_selection.new(
                                              action='content',
                                              course_id=course_id,
                                              topic_id=topic_id,
                                              page=page)))
        
    if topic.main_text_webapp_readuser:
        buttons.append(types.InlineKeyboardButton(text=f"{checkmark}Веб",
                                          web_app=types.WebAppInfo(url=f"https://educationalbot.engsdrilling.ru/api/testing-testing_module/course_topic/{topic_id}/main_text/")))
    
    # if topic.pdf_file_readuser:
    #     buttons.append(types.InlineKeyboardButton(
    #         text=f"{checkmark}PDF",
    #         web_app=types.WebAppInfo(
    #             url=f"https://educationalbot.engsdrilling.ru/api/testing-testing_module/course_topic/{topic_id}/pdf/"
    #         )
    #     ))
    if topic.pdf_file_readuser:
        buttons.append(types.InlineKeyboardButton(
            text=f"{checkmark}PDF",
            callback_data=pdf_callback.new(course_id=course_id, topic_id=topic_id)
        ))

    if topic.audio_file_readuser:
        buttons.append(types.InlineKeyboardButton(
            text=f"{checkmark}Аудио",
            callback_data=audio_callback.new(course_id=course_id, topic_id=topic_id)
        ))

    if topic.video_file_readuser:
        buttons.append(types.InlineKeyboardButton(
            text=f"{checkmark}Видео",
            callback_data=video_callback.new(course_id=course_id, topic_id=topic_id)
        ))

    # https://127.0.0.1:8000/
    # https://educationalbot.engsdrilling.ru/

    kb.row(*buttons)

    kb.add(types.InlineKeyboardButton(text=_('← к списку разделов'),
                                      callback_data=topic_menu.new(
                                          info='topic',
                                          course_id=course_id,
                                          topic_id=topic_id,
                                          subtopic_id='-',
                                          page=0)))

    return kb, mark_safe(content_pages[page]), topic.image_course_topic


@sync_to_async
def content_menu_kb_generator(course_id, topic_id, page=0):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    topic = apps.get_model('educational_module.CourseTopic').objects.get(id=topic_id)
    content = f'<b>{topic.main_text}</b>'

    content_pages = paginate_text(content)
    # Очистка только содержимого страниц
    content_pages = [remove_unsupported_html_tags(page) for page in content_pages]

    total_pages = len(content_pages)

    current_page_text = f'{page + 1} из {total_pages}'

    buttons = []

    if len(content_pages) > 1:
        if page > 0:
            buttons.append(types.InlineKeyboardButton(text="назад", callback_data=content_selection.new(
                action='content', course_id=course_id, topic_id=topic_id, page=page-1)))
        buttons.append(types.InlineKeyboardButton(text=current_page_text, callback_data=content_selection.new(
                action='ignore', course_id=course_id, topic_id=topic_id, page=page)))
        if page < len(content_pages) - 1:
            buttons.append(types.InlineKeyboardButton(text="вперед", callback_data=content_selection.new(
                action='content', course_id=course_id, topic_id=topic_id, page=page+1)))
            
    kb.row(*buttons)

    kb.add(types.InlineKeyboardButton(text=_('← к разделу'),
                                      callback_data=content_selection.new(
                                          action='select_content',
                                          course_id=course_id,
                                          topic_id=topic_id,
                                          page=0)))

    return kb, mark_safe(content_pages[page]), topic.image_course_topic
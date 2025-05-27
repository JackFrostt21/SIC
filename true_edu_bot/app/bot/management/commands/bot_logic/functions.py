from asgiref.sync import sync_to_async
from aiogram import types
import os
from django.conf import settings
import re
from aiogram.types import CallbackQuery

from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.loader import dp
from app.bot.models.telegram_user import TelegramUser
from app.bot.models import UserTest

from app.educational_module.models import Company
from app.bot.management.commands.bot_logic.callbackfactory import topic_menu, begin_test, content_selection


i18n = setup_middleware(dp)
_ = i18n.gettext


@sync_to_async
def user_exists(user_id, username, mention):
    try:
        company_name = "ЭНГС"
        company_instance = Company.objects.get(name=company_name)
        user, created = TelegramUser.objects.get_or_create(user_id=user_id,
                                                        defaults={
                                                            'user_name': username,
                                                            'tg_mention': mention,
                                                            'company': company_instance
                                                        })
        user.testing_process = False
        user.save()
        return user.state

    except Exception as e:
        print(e)


@sync_to_async
def user_set_language(user_id, language):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        user.language = language
        user.save()
    except Exception as e:
        print(e)


@sync_to_async
def user_get_tools(user_id):
    return TelegramUser.objects.get(user_id=user_id)


@sync_to_async
def user_change_test_status(user_id):
    user = TelegramUser.objects.get(user_id=user_id)
    user.testing_process = False
    user.save()


@sync_to_async
def load_bot_logo(tag, user_id):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        company = user.company

        if not company:
            raise ValueError('Компания не указана')

        if tag == 'main_menu_logo':
            photo = company.image_start_company.path if company.image_start_company else None
        elif tag == 'welcome_logo':
            photo = company.image_start_company.path if company.image_start_company else None
        elif tag == 'user_blocked_logo':
            photo = company.logo_company.path if company.logo_company else None
        else:
            raise ValueError("Unknown tag")
        
        if not photo:
            raise ValueError('Изображение не указано')

        content = " "
        title = "Добро пожаловать"

        if user.language:
            tag = f'{tag}_{user.language}'
        else:
            tag = f'{tag}_ru'

        return title, content, photo
    except Exception as e:
        print(e)
        content = ' '
        title = ' '
        photo = 'start_images/good_luck.png'
        return title, content, photo

@sync_to_async
def load_test_result_image(user_id, test_passed):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        company = user.company

        if not company:
            raise ValueError('Компания не указана')

        if test_passed:
            photo = company.image_test_passed.path if company.image_test_passed else None
        else:
            photo = company.image_test_failed.path if company.image_test_failed else None

        if not photo:
            raise ValueError('Изображение не указано')

        return photo
    except Exception as e:
        print(e)
        return None
    
@sync_to_async
def load_test_start_image(user_id):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        company = user.company

        if not company:
            raise ValueError('Компания не указана')

        photo = company.image_test_start.path if company.image_test_start else None

        if not photo:
            raise ValueError('Изображение не указано')

        return photo
    except Exception as e:
        print(e)
        return None
    

MAX_CAPTION_LENGTH = 1024
def paginate_text(text, max_length=MAX_CAPTION_LENGTH):
    pages = []
    current_page = ""
    current_length = 0
    tag_stack = []

    def add_page():
        nonlocal current_page, current_length
        pages.append(current_page.strip())
        current_page = ""
        current_length = 0

    tag_re = re.compile(r'<(/?)(\w+)[^>]*>')

    for part in re.split(r'(\s+)', text):
        for match in tag_re.finditer(part):
            if match:
                tag = match.group(2)
                if match.group(1):  # Closing tag
                    if tag_stack and tag_stack[-1] == tag:
                        tag_stack.pop()
                else:  # Opening tag
                    tag_stack.append(tag)

        if current_length + len(part) > max_length:
            add_page()
            if tag_stack:
                for tag in tag_stack:
                    current_page += f'<{tag}>'
                current_length += sum(len(f'<{tag}>') for tag in tag_stack)

        current_page += part
        current_length += len(part)

    if current_page.strip():
        add_page()

    for i in range(len(pages)):
        open_tags = []
        close_tags = []
        for tag in tag_stack:
            open_tags.append(f'<{tag}>')
            close_tags.insert(0, f'</{tag}>')
        pages[i] = ''.join(open_tags) + pages[i] + ''.join(close_tags)

    return pages


def remove_unsupported_html_tags(content):
    """Remove unsupported HTML tags, leaving only supported ones."""
    # Список поддерживаемых HTML тегов
    supported_tags = ['<b>', '</b>', '<i>', '</i>', '<u>', '</u>', '<a>', '</a>', '<code>', '</code>', '<pre>', '</pre>']

    # Функция для удаления тегов
    def clean_html(content):
        tag_re = re.compile(r'<[^>]+>')
        cleaned_content = tag_re.sub(lambda match: match.group(0) if any(tag in match.group(0) for tag in supported_tags) else '', content)
        return cleaned_content

    cleaned_content = clean_html(content)

    # Проверка на соответствие открывающих и закрывающих тегов
    tag_stack = []
    tag_re = re.compile(r'<(/?)(\w+)>')
    for match in tag_re.finditer(cleaned_content):
        tag = match.group(2)
        if match.group(1) == '/':  # Closing tag
            if tag_stack and tag_stack[-1] == tag:
                tag_stack.pop()
            else:
                print(f"Unmatched closing tag: {tag}")
        else:  # Opening tag
            tag_stack.append(tag)

    if tag_stack:
        for tag in reversed(tag_stack):
            cleaned_content += f'</{tag}>'

    return cleaned_content


@sync_to_async
def clear_user_test(user_id, course_id):
    try:
        user_test, created = UserTest.objects.get_or_create(user__user_id=user_id, training__id=course_id)
        user_test.user_answer = {"results": []}
        user_test.save()
    except Exception as e:
        print(f"An error occurred while clearing user test: {e}")


@sync_to_async
def get_selected_answers(user_id, course_id, question_id):
    try:
        user_test = UserTest.objects.get(user__user_id=user_id, training__id=course_id)
        current_user_answer = user_test.user_answer

        existing_result = next((result for result in current_user_answer["results"] if result["question_id"] == str(question_id)), None)

        if existing_result:
            return existing_result["answer_id"]
        else:
            return []
    except UserTest.DoesNotExist:
        return []        
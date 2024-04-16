from asgiref.sync import sync_to_async

from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.loader import dp
from app.bot.models.bot_settings import SetsListParameter
from app.bot.models.telegram_user import TelegramUser
from app.core.methods import decorator_debug

i18n = setup_middleware(dp)
_ = i18n.gettext

"""---------------------------------------Base Functions---------------------------------------"""


@sync_to_async
@decorator_debug
def user_exists(user_id, username, mention):
    try:
        user, info = TelegramUser.objects.get_or_create(user_id=user_id,
                                                        defaults={
                                                            'user_name': username,
                                                            'tg_mention': mention,
                                                        })
        user.testing_process = False
        user.save()
        return user.state

    except Exception as e:
        print(e)


@sync_to_async
@decorator_debug
def user_set_language(user_id, language):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        user.language = language
        user.save()
    except Exception as e:
        print(e)


"""---------------------------------------Settings---------------------------------------"""


@sync_to_async
@decorator_debug
def user_get_tools(user_id):
    return TelegramUser.objects.get(user_id=user_id)


@sync_to_async
@decorator_debug
def user_change_test_status(user_id):
    user = TelegramUser.objects.get(user_id=user_id)
    user.testing_process = False
    user.save()


"""---------------------------------------Old Functions---------------------------------------"""


# @sync_to_async
# def load_bot_logo():
#     try:
#         content = '*'
#         title = '*'
#         # media = types.InputFile(f'media/admin/icons/bot_logo.png')
#         photo = f'admin/icons/bot_logo.png'
#         return title, content, photo
#     except Exception as e:
#         print(e)

@sync_to_async
@decorator_debug
def load_bot_logo(tag, user_id):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        if user.language:
            tag = f'{tag}_{user.language}'
        else:
            tag = f'{tag}_ru'
        logo = SetsListParameter.objects.get(tag=tag)
        content = logo.description
        title = logo.value
        photo = logo.photo
        return title, content, photo
    except Exception as e:
        print(e)
        content = '*'
        title = '*'
        photo = 'settings/logo-ngs-all.png'
        return title, content, photo

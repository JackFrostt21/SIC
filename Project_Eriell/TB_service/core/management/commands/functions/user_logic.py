from asgiref.sync import sync_to_async
from core.models import TelegramUser
from TB_service import method


@sync_to_async
@method.decorator_debug
def user_exists(user_id: int, username: str, mention: str) -> object:
    try:
        user, info = TelegramUser.objects.get_or_create(user_id=user_id,
                                                        defaults={
                                                            'user_name': username,
                                                            'tg_mention': mention,
                                                        })
        user.testing_process = False
        user.save()
        return user

    except Exception as e:
        print(e)

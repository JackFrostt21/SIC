from aiogram.utils.callback_data import CallbackData
from asgiref.sync import sync_to_async

from app.bot.models import UserTest
from app.core.methods import decorator_debug
from app.educational_module.models import CourseTopic, TrainingCourse

self_progress_menu = CallbackData('self_progress_menu', )


@sync_to_async
@decorator_debug
def progress_result(user_id):
    training_id = TrainingCourse.objects.filter(user__user_id=user_id).values_list(
        "id", flat=True)
    result_test = UserTest.objects.filter(user__user_id=user_id, training__id__in=[training_id]).values_list(
        "training__title", "quantity_correct", "quantity_not_correct")

    text = ""

    for item in result_test:
        title, value1, value2 = item
        text += (f"<i>{title}</i> \n"
                 f"<b>Верных ответов:</b> {value1}%\n"
                 f"<b>Неверных ответов: </b> {value2}%\n\n")

    return f"{text}"

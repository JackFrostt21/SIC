from aiogram.utils.callback_data import CallbackData
from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from app.bot.models import UserTest
from app.educational_module.models import TrainingCourse

@sync_to_async
def progress_result(user_id):
    training_ids = TrainingCourse.objects.filter(user__user_id=user_id).values_list("id", flat=True)
    result_tests = UserTest.objects.filter(user__user_id=user_id, training__id__in=training_ids)

    text = ""

    for result_test in result_tests:
        title = result_test.training.title
        value1 = result_test.quantity_correct
        complete = result_test.complete
        status_image = "✓ " if complete else "✕ "

        text += (
                f"{status_image}<i>{title}</i> {value1}%\n\n"
                )

    return f"{text}"
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from app.bot.models.telegram_user import TelegramUser
from app.bot.models.testing_module import UserTest
from app.educational_module.models import AnswerOption, TrainingCourse, TopicQuestion
from ...functions import load_bot_logo
from ...lang_middleware import setup_middleware
from ....loader import dp

test_menu = CallbackData('test_menu', 'info', 'course_id', 'topic_id', 'question_id', 'current_question_index',
                         'answer_id')

i18n = setup_middleware(dp)
_ = i18n.gettext


@sync_to_async
def training_course_menu_kb_generator(user_id):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    user = TelegramUser.objects.get(user_id=user_id)
    training_course = TrainingCourse.objects.filter(user=user)
    content = _("First Complete the training")
    if training_course:
        [kb.add(types.InlineKeyboardButton(text=f'{training.title}',
                                           callback_data=test_menu.new(
                                               info='question',
                                               course_id=training.id,
                                               topic_id="-",
                                               question_id='-',
                                               answer_id='-',
                                               current_question_index='-'))) for training in training_course]

        return kb, " "
    else:
        return kb, content


@sync_to_async
def question_kb_generator(user_id, course_id):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    user = TelegramUser.objects.get(user_id=user_id)

    questions = TopicQuestion.objects.filter(training__id=course_id, is_actual=True).order_by("id")[
        user.current_question_index]
    current_question_index = user.current_question_index
    user.testing_process = True
    user.save()

    try:
        answer_option = questions.answer_options.filter(topic_question__id=questions.id, is_actual=True)

        text = ""
        for title, index in zip(answer_option, ("A", "B", "C", "D",)):
            text += f"<b>{index})</b> {title.text}\n\n"

        [kb.add(types.InlineKeyboardButton(text=f"{answer.number}",
                                           callback_data=test_menu.new(
                                               info='answer',
                                               course_id=course_id,
                                               topic_id="-",
                                               current_question_index=current_question_index,
                                               answer_id=answer.id,
                                               question_id=questions.id))) for answer in answer_option]

        content = (f'<b>{questions.title}</b>'
                   f'\n\n<i>{questions.topic}</i>'
                   f'\n\n{text}')

        return kb, content


    except Exception as e:
        print(e)


@sync_to_async
def answer_kb_generator(current_question_index, topic_id, user_id, course_id):
    user = TelegramUser.objects.get(user_id=user_id)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[], row_width=2)

    try:
        questions = TopicQuestion.objects.filter(training__id=course_id, is_actual=True).order_by("id")[
            int(current_question_index)]
        current_question_index = int(current_question_index)
        user.current_question_index = current_question_index
        user.save()

        answer_option = questions.answer_options.filter(topic_question__id=questions.id, is_actual=True)

        text = ""
        for title, index in zip(answer_option, ("A", "B", "C", "D",)):
            text += f"<b>{index})</b> {title.text}\n\n"

        [kb.add(types.InlineKeyboardButton(text=f"{answer.number}",
                                           callback_data=test_menu.new(
                                               info='answer',
                                               course_id=course_id,
                                               topic_id=topic_id,
                                               current_question_index=current_question_index,
                                               answer_id=answer.id,
                                               question_id=questions.id))) for answer in answer_option]

        content = (f'<b>{questions.title}</b>'
                   f'\n\n<i>{questions.topic}</i>'
                   f'\n\n{text}')

        return kb, content

    except IndexError:
        user.testing_process = False
        user.current_question_index = 1
        user.save()

        content = "count_correct_answer"
        return kb, content


@dp.callback_query_handler(test_menu.filter())
async def test_menu_handler(callback: CallbackQuery, callback_data: dict):
    try:
        kb = None
        sub_content = ''
        match callback_data.get('info'):
            case 'question':
                kb, sub_content = await question_kb_generator(user_id=callback.from_user.id,
                                                              course_id=callback_data.get("course_id"))

            case 'answer':
                current_question_index = int(callback_data.get("current_question_index"))
                current_question_index += 1
                kb, sub_content = await answer_kb_generator(current_question_index,
                                                            callback_data.get("topic_id"),
                                                            callback.from_user.id,
                                                            callback_data.get("course_id"))

                await save_user_answer(user_id=callback.from_user.id, answer_id=callback_data.get("answer_id"),
                                       question_id=callback_data.get("question_id"),
                                       course_id=callback_data.get("course_id"))

        sub_content = await counting_correct_answers(callback.from_user.id, callback_data.get("course_id")) \
            if sub_content == 'count_correct_answer' else sub_content

        title, content, photo = await load_bot_logo('tag', callback.from_user.id)
        with open(f'media/{photo}', 'rb') as file:
            photo = types.InputMediaPhoto(file, caption=f'{content}\n{sub_content}')
            await callback.message.edit_media(media=photo, reply_markup=kb)
            file.close()
    except Exception as e:
        print(e)


@sync_to_async
def save_user_answer(user_id, answer_id, question_id, course_id):
    try:
        is_correct = AnswerOption.objects.get(id=answer_id).is_correct

        user_test, created = UserTest.objects.get_or_create(user__user_id=user_id, training__id=course_id)
        current_user_answer = user_test.user_answer

        new_result = {"question_id": question_id, "answer_id": answer_id, "is_correct": is_correct}
        current_user_answer["results"].append(new_result)

        user_test.user_answer = current_user_answer
        user_test.save()

    except ObjectDoesNotExist as e:
        print(f"Object not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


@sync_to_async
def counting_correct_answers(user_id, course_id):
    quantity_correct = 0
    quantity_not_correct = 0

    result_test = UserTest.objects.get(user__user_id=user_id, training__id=course_id).user_answer
    for i in result_test["results"]:
        if i["is_correct"]:
            quantity_correct += 1
        else:
            quantity_not_correct += 1

    sum_answer = quantity_correct + quantity_not_correct

    correct_percent = 100 * quantity_correct // sum_answer
    correct_not_percent = 100 * quantity_not_correct // sum_answer

    UserTest.objects.update_or_create(user__user_id=user_id, training__id=course_id, defaults={
        "quantity_correct": correct_percent,
        "quantity_not_correct": correct_not_percent   ###Кажется делает левые записи, проверить, добавляет в user_answer все варианты доступных ответов
    })
    training_title = TrainingCourse.objects.get(id=course_id).title

    return (f"Ваш результат по курсу <b>{training_title}</b>\n\n"
            f"<b>Верных ответов:</b> {correct_percent}%\n"
            f"<b>Не верных ответов:</b> {correct_not_percent}%")

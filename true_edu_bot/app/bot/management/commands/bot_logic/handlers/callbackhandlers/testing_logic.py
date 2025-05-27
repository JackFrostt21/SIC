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
from app.bot.management.commands.bot_logic.callbackfactory import test_menu
from app.bot.management.commands.bot_logic.kb.test_kb import (
    question_kb_generator,
    answer_kb_generator,
)

i18n = setup_middleware(dp)
_ = i18n.gettext


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
        # Получаем вопрос и проверяем, является ли он множественным выбором
        question = TopicQuestion.objects.get(id=question_id)
        is_multiple_choice = question.is_multiple_choice

        # Получаем все правильные ответы для данного вопроса
        correct_answers = list(AnswerOption.objects.filter(topic_question_id=question_id, is_correct=True).values_list('id', flat=True))
        correct_answers = list(map(str, correct_answers))
        answer_id = str(answer_id)

        user_test, created = UserTest.objects.get_or_create(user__user_id=user_id, training__id=course_id)
        current_user_answer = user_test.user_answer

        # Найти существующий результат для данного вопроса
        existing_result = next((result for result in current_user_answer["results"] if result["question_id"] == question_id), None)

        if existing_result:
            if is_multiple_choice:
                # Для множественного выбора добавляем или удаляем ответы
                if answer_id in existing_result["answer_id"]:
                    existing_result["answer_id"].remove(answer_id)
                else:
                    existing_result["answer_id"].append(answer_id)
            else:
                # Для одиночного выбора заменяем ответ
                existing_result["answer_id"] = [answer_id]

            # Проверяем корректность ответов
            if set(existing_result["answer_id"]) == set(correct_answers):
                existing_result["is_correct"] = True
            else:
                existing_result["is_correct"] = False
        else:
            # Добавить новый результат
            is_correct = set([answer_id]) == set(correct_answers) if not is_multiple_choice else False
            new_result = {"question_id": question_id, "answer_id": [answer_id], "is_correct": is_correct}
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

    user_test = UserTest.objects.get(user__user_id=user_id, training__id=course_id)
    result_test = user_test.user_answer
    for i in result_test["results"]:
        if i["is_correct"]:
            quantity_correct += 1
        else:
            quantity_not_correct += 1

    sum_answer = quantity_correct + quantity_not_correct

    correct_percent = 100 * quantity_correct // sum_answer if sum_answer else 0
    correct_not_percent = 100 * quantity_not_correct // sum_answer if sum_answer else 0

    # Определяем успешность прохождения теста
    training_course = TrainingCourse.objects.get(id=course_id)
    is_complete = correct_percent >= training_course.min_test_percent_course
    if user_test.quantity_correct is None or correct_percent > user_test.quantity_correct:
        user_test.complete = is_complete
        user_test.quantity_correct = correct_percent
        user_test.quantity_not_correct = correct_not_percent
        user_test.save()

    training_title = training_course.title
    result_message = (
        f"Ваш результат по курсу <b>{training_title}</b>\n\n"
        f"<b>Верных ответов:</b> {correct_percent}%\n"
        f"<b>Не верных ответов:</b> {correct_not_percent}%\n\n"
    )
    if is_complete:
        result_message += "Поздравляю, вы успешно сдали тест"
    else:
        result_message += "К сожалению, вы не сдали тест"

    return result_message
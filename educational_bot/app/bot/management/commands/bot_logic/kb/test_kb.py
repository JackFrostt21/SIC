from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from app.bot.models.telegram_user import TelegramUser
from app.bot.models.testing_module import UserTest
from app.educational_module.models import AnswerOption, TrainingCourse, TopicQuestion
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.loader import dp
from app.bot.management.commands.bot_logic.callbackfactory import test_menu


i18n = setup_middleware(dp)
_ = i18n.gettext

# @sync_to_async
# def training_course_menu_kb_generator(user_id):
#     kb = types.InlineKeyboardMarkup(inline_keyboard=[])
#     user = TelegramUser.objects.get(user_id=user_id)
#     training_course = TrainingCourse.objects.filter(user=user)
#     content = _("First Complete the training")
#     if training_course:
#         [kb.add(types.InlineKeyboardButton(text=f'{training.title}',
#                                            callback_data=test_menu.new(
#                                                info='question',
#                                                course_id=training.id,
#                                                topic_id="-",
#                                                question_id='-',
#                                                answer_id='-',
#                                                current_question_index='-'))) for training in training_course]

#         return kb, " "
#     else:
#         return kb, content


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

        [kb.add(types.InlineKeyboardButton(text=f"{answer.text}",
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

        [kb.add(types.InlineKeyboardButton(text=f"{answer.text}",
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
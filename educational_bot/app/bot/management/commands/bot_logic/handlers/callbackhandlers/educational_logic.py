from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from asgiref.sync import sync_to_async
from django.apps import apps

from app.bot.models import UserTest
from app.bot.models.telegram_user import TelegramUser
from app.educational_module.models import TopicQuestion, TrainingCourse
from .testing_logic import counting_correct_answers, save_user_answer
from ...functions import load_bot_logo
from ...lang_middleware import setup_middleware
from ....loader import dp

i18n = setup_middleware(dp)
_ = i18n.gettext

topic_menu = CallbackData('topic_menu', 'info', 'course_id', 'topic_id', 'subtopic_id')
begin_test = CallbackData('begin_test', "info", "course_id", "question_id", "next_question", "answer_id")

result_dict = {"results": []}


@sync_to_async
def course_menu_kb_generator():
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    menu_list = apps.get_model('educational_module.TrainingCourse').objects.filter(is_actual=True)
    [kb.add(types.InlineKeyboardButton(text=f'{i.title}',
                                       callback_data=topic_menu.new(
                                           info='topic',
                                           course_id=i.id,
                                           topic_id='-',
                                           subtopic_id='-'))) for i in menu_list]

    return kb


@sync_to_async
def topic_menu_kb_generator(course_id):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    course = apps.get_model('educational_module.TrainingCourse').objects.get(id=course_id)

    content = f'<b>{course.title}</b>\n<i>{course.description}</i>'
    menu_list = apps.get_model('educational_module.CourseTopic').objects.filter(is_actual=True,
                                                                                training_course=course_id)
    [kb.add(types.InlineKeyboardButton(text=f'{i.title}',
                                       callback_data=topic_menu.new(
                                           info='subtopic',
                                           course_id=course_id,
                                           topic_id=i.id,
                                           subtopic_id='-'))) for i in menu_list]
    kb.add(types.InlineKeyboardButton(text=_('go_test'),
                                      callback_data=begin_test.new(
                                          info="on_test",
                                          course_id=course_id,
                                          question_id=0,
                                          next_question=0,
                                          answer_id='-'

                                      )))
    kb.add(types.InlineKeyboardButton(text=_('btn_back'),
                                      callback_data=topic_menu.new(
                                          info='course',
                                          course_id=course_id,
                                          topic_id='-',
                                          subtopic_id='-')))
    return kb, content


@sync_to_async
def subtopic_menu_kb_generator(course_id, topic_id):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    topic = apps.get_model('educational_module.CourseTopic').objects.get(id=topic_id)
    content = f'<b>{topic.title}</b>\n<i>{topic.description}</i>\n<b>{topic.main_text}</b>'
    menu_list = apps.get_model('educational_module.Subtopic').objects.filter(is_actual=True,
                                                                             course_topic=topic_id)
    [kb.add(types.InlineKeyboardButton(text=f'{i.title}',
                                       callback_data=topic_menu.new(
                                           info='in_subtopic',
                                           course_id=course_id,
                                           topic_id=topic_id,
                                           subtopic_id=i.id))) for i in menu_list]
    kb.add(types.InlineKeyboardButton(text=_('btn_back'),
                                      callback_data=topic_menu.new(
                                          info='topic',
                                          course_id=course_id,
                                          topic_id=topic_id,
                                          subtopic_id='-')))
    return kb, content


@sync_to_async
def in_subtopic_menu_kb_generator(course_id, topic_id, subtopic_id):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    subtopic = apps.get_model('educational_module.Subtopic').objects.get(id=subtopic_id)
    content = f'<b>{subtopic.title}</b>\n<i>{subtopic.description}</i>\n<b>{subtopic.main_text}</b>'
    kb.add(types.InlineKeyboardButton(text=_('btn_back'),
                                      callback_data=topic_menu.new(
                                          info='subtopic',
                                          course_id=course_id,
                                          topic_id=topic_id,
                                          subtopic_id='-')))
    return kb, content


@sync_to_async
def get_questions(course_id, question_id, next_question, user_id):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[], row_width=3)

    user = TelegramUser.objects.get(user_id=user_id)

    course = TrainingCourse.objects.get(id=course_id)
    course.user.add(user)

    UserTest.objects.get_or_create(user=TelegramUser.objects.get(user_id=user_id),
                                   training=TrainingCourse.objects.get(id=course_id)
                                   )

    try:

        if question_id == "0":

            user.testing_process = True
            user.save()

            current_index_question = user.current_question_index
            question = TopicQuestion.objects.filter(training__id=course_id, is_actual=True).order_by("id")[
                current_index_question]
            answers = question.answer_options.all()

            text = ""

            for answer, index in zip(answers, ("A", "B", "C", "D",)):
                kb.add(types.InlineKeyboardButton(text=f"{answer.number}",
                                                  callback_data=begin_test.new(
                                                      info='run_test',
                                                      course_id=course_id,
                                                      next_question=current_index_question + 1,
                                                      question_id=question.id,
                                                      answer_id=answer.id)))

                text += f"<b>{index})</b> {answer.text}\n\n"

            content = (f'<b>{question.title}</b>'
                       f'\n\n<i>{question.topic}</i>'
                       f'\n\n{text}')
            return kb, content

        else:
            question = TopicQuestion.objects.filter(training__id=course_id, is_actual=True).order_by("id")[
                int(next_question)]
            curr_question_order = int(next_question)
            user.current_question_index = curr_question_order
            user.save()
            answers = question.answer_options.all()
            text = ""
            for answer, index in zip(answers, ("A", "B", "C", "D",)):
                kb.add(types.InlineKeyboardButton(text=f"{answer.number}",
                                                  callback_data=begin_test.new(
                                                      info='run_test',
                                                      course_id=course_id,
                                                      next_question=curr_question_order + 1,
                                                      question_id=question.id,
                                                      answer_id=answer.id)))

                text += f"<b>{index})</b> {answer.text}\n\n"

            content = (f'<b>{question.title}</b>'
                       f'\n\n<i>{question.topic}</i>'
                       f'\n\n{text}')

            return kb, content

    except IndexError as Ex:
        print(Ex)
        user.current_question_index = 1

        user.testing_process = False
        user.save()

        content = "count_correct_answer"
        return kb, content


@dp.callback_query_handler(topic_menu.filter())
async def topic_menu_handler(callback: CallbackQuery, callback_data: dict):
    try:
        kb = None
        sub_content = ''
        match callback_data.get('info'):


            case 'in_subtopic':
                kb, sub_content = await in_subtopic_menu_kb_generator(callback_data.get('course_id'),
                                                                      callback_data.get('topic_id'),
                                                                      callback_data.get('subtopic_id'))
            case 'subtopic':
                kb, sub_content = await subtopic_menu_kb_generator(callback_data.get('course_id'),
                                                                   callback_data.get('topic_id'))
            case 'topic':
                kb, sub_content = await topic_menu_kb_generator(callback_data.get('course_id'))
            case 'course':
                kb = await course_menu_kb_generator()
        title, content, photo = await load_bot_logo('tag', callback.from_user.id)
        kb.add(types.InlineKeyboardButton(text=_('btn_close'),
                                          callback_data='btn_done', ))

        with open(f'media/{photo}', 'rb') as file:
            photo = types.InputMediaPhoto(file, caption=f'{content}\n{sub_content}')
            await callback.message.edit_media(media=photo, reply_markup=kb)
            file.close()
    except Exception as e:
        print(e)


@dp.callback_query_handler(begin_test.filter())
async def get_test(callback: CallbackQuery, callback_data: dict):
    try:
        kb = None
        sub_content = ''
        match callback_data.get("info"):

            case "on_test":
                kb, sub_content = await get_questions(callback_data.get("course_id"),
                                                      callback_data.get("question_id"),
                                                      callback_data.get('next_question'),
                                                      callback.from_user.id)

            case "run_test":

                kb, sub_content = await get_questions(callback_data.get("course_id"),
                                                      callback_data.get("question_id"),
                                                      callback_data.get('next_question'),
                                                      callback.from_user.id)

                await save_user_answer(user_id=callback.from_user.id,
                                       answer_id=callback_data.get("answer_id"),
                                       question_id=callback_data.get("question_id"),
                                       course_id=callback_data.get("course_id"))

        sub_content = await counting_correct_answers(callback.from_user.id, callback_data.get("course_id")) \
            if sub_content == 'count_correct_answer' else sub_content

        title, content, photo = await load_bot_logo('tag', callback.from_user.id)
        kb.add(types.InlineKeyboardButton(text=_('btn_close'),
                                          callback_data='btn_done', ))

        with open(f'media/{photo}', 'rb') as file:
            photo = types.InputMediaPhoto(file, caption=f'{content}\n{sub_content}')
            await callback.message.edit_media(media=photo, reply_markup=kb)
            file.close()

    except IndexError as e:
        print(e)

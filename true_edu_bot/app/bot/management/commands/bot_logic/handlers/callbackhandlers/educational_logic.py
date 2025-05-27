from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from asgiref.sync import sync_to_async
from django.apps import apps
import re
from django.db.models import Q
import os
from django.utils.safestring import mark_safe

from app.bot.models import UserTest
from app.bot.models.telegram_user import TelegramUser, UserRead
from app.educational_module.models import TopicQuestion, TrainingCourse, CourseTopic
from .testing_logic import counting_correct_answers, save_user_answer
from ...functions import (
    load_bot_logo,
    load_test_result_image,
    load_test_start_image,
    paginate_text,
    remove_unsupported_html_tags,
    clear_user_test,
    get_selected_answers,
)
from ...lang_middleware import setup_middleware
from ....loader import dp
from app.bot.management.commands.bot_logic.kb.kb import (
    course_menu_kb_generator,
    topic_menu_kb_generator,
    subtopic_menu_kb_generator,
    content_menu_kb_generator,
)
from app.bot.management.commands.bot_logic.callbackfactory import (
    topic_menu,
    begin_test,
    content_selection,
    pdf_callback,
    audio_callback,
    video_callback
)

i18n = setup_middleware(dp)
_ = i18n.gettext


@dp.callback_query_handler(topic_menu.filter(info="course"))
async def back_to_courses(callback: CallbackQuery, callback_data: dict):
    user_id = callback.from_user.id
    user = await sync_to_async(TelegramUser.objects.get)(user_id=user_id)
    kb = await course_menu_kb_generator(user)

    image_path = user.company.image_list_courses.path
    if os.path.exists(image_path):
        media = types.InputFile(image_path)
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=media,
            caption=_("Список ваших курсов"),
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await callback.message.delete()
        await callback.message.answer(
            _("Список ваших курсов"), parse_mode="HTML", reply_markup=kb
        )


@sync_to_async
def get_questions(
    course_id, question_id, next_question, user_id, selected_answers=None
):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[], row_width=1)

    user = TelegramUser.objects.get(user_id=user_id)
    course = TrainingCourse.objects.get(id=course_id)
    course.user.add(user)

    UserTest.objects.get_or_create(
        user=TelegramUser.objects.get(user_id=user_id),
        training=TrainingCourse.objects.get(id=course_id),
    )
    if selected_answers is None:
        selected_answers = []

    try:
        questions = list(
            TopicQuestion.objects.filter(
                training__id=course_id, is_actual=True
            ).order_by("id")
        )
        total_questions = len(questions)
        next_question = int(next_question)
        if next_question < 0 or next_question >= total_questions:
            return None, None

        question = questions[next_question]
        curr_question_order = next_question
        user.current_question_index = curr_question_order
        user.save()
        answers = question.answer_options.all()

        # Проверяем, является ли вопрос множественным выбором
        is_multiple_choice = question.is_multiple_choice
        # Определяем символы для кнопок
        if is_multiple_choice:
            unselected_symbol = "◻️"
            selected_symbol = "🟩"
        else:
            unselected_symbol = "⚪"
            selected_symbol = "🟢"

        text = ""
        for answer, index in zip(answers, ("A", "B", "C", "D",)):
            button_text = f"{unselected_symbol} {answer.number}"
            if str(answer.id) in selected_answers:
                button_text = f"{selected_symbol} {answer.number}"
            kb.add(
                types.InlineKeyboardButton(
                    text=button_text,
                    callback_data=begin_test.new(
                        info="select_answer",
                        course_id=course_id,
                        question_id=question.id,
                        next_question=curr_question_order,
                        answer_id=answer.id,
                    ),
                )
            )
            text += f"<b>{index})</b> {answer.text}\n\n"

        # Добавляем подпись после вариантов ответа
        if is_multiple_choice:
            caption_text = "Выберите несколько правильных ответов"
        else:
            caption_text = "Выберите 1 правильный ответ"

        content = (
            f"<b>Тестирование</b>"
            f"\n\nВопрос ({curr_question_order + 1} из {total_questions})"
            f"\n\n<i>{question.title}</i>"
            f"\n\n{text}"
            f"\n{caption_text}"
        )

        nav_buttons = []

        # Добавляем кнопку "вперед" только если выбран хотя бы один ответ
        if curr_question_order < total_questions - 1 and selected_answers:
            nav_buttons.append(
                types.InlineKeyboardButton(
                    text="🠆 вперед",
                    callback_data=begin_test.new(
                        info="next_question",
                        course_id=course_id,
                        question_id=question.id,
                        next_question=curr_question_order + 1,
                        answer_id="-",
                    ),
                )
            )

        if nav_buttons:
            kb.row(*nav_buttons)

        kb.add(
            types.InlineKeyboardButton(
                text="Завершить тестирование",
                callback_data=begin_test.new(
                    info="finish_test",
                    course_id=course_id,
                    question_id=question.id,
                    next_question="-",
                    answer_id="-",
                ),
            )
        )

        return kb, content

    except IndexError as Ex:
        print(Ex)
        user.current_question_index = 1
        user.testing_process = False
        user.save()

        return None, None


@dp.callback_query_handler(begin_test.filter(info="on_test"))
async def start_test(callback: CallbackQuery, callback_data: dict):
    try:
        user_id = callback.from_user.id
        course_id = callback_data.get("course_id")

        # Очистка текущих результатов перед началом теста
        await clear_user_test(user_id, course_id)

        # Загрузка изображения из модели TrainingCourse
        training_course = await sync_to_async(TrainingCourse.objects.get)(id=course_id)
        if training_course.image_course:
            start_image_path = training_course.image_course.path
            media = types.InputFile(start_image_path)
        else:
            media = None

        kb, sub_content = await get_questions(
            course_id, callback_data.get("question_id"), 0, user_id
        )

        if kb:
            content = ""
            if media:
                photo = types.InputMediaPhoto(
                    media, caption=f"{content}\n{sub_content}"
                )
                await callback.message.edit_media(media=photo, reply_markup=kb)
            else:
                # Если изображения нет, просто обновляем текст и клавиатуру
                await callback.message.edit_caption(caption=f"{content}\n{sub_content}", reply_markup=kb)
        else:
            if sub_content:
                await callback.message.answer(sub_content)

    except Exception as e:
        print(e)



@dp.callback_query_handler(begin_test.filter())
async def handle_test_navigation(callback: CallbackQuery, callback_data: dict):
    try:
        kb = None
        sub_content = ""
        user_id = callback.from_user.id
        course_id = callback_data.get("course_id")
        question_id = callback_data.get("question_id")
        next_question = callback_data.get("next_question")

        # Получение изображения из TrainingCourse
        training_course = await sync_to_async(TrainingCourse.objects.get)(id=course_id)
        if training_course.image_course:
            image_path = training_course.image_course.path
            media = types.InputFile(image_path)
        else:
            media = None

        match callback_data.get("info"):
            case "on_test":
                await clear_user_test(user_id, course_id)  # Очистка текущих результатов
                selected_answers = []
                kb, sub_content = await get_questions(
                    course_id, question_id, 0, user_id, selected_answers
                )

            case "select_answer":
                answer_id = callback_data.get("answer_id")
                question_id = callback_data.get("question_id")

                # Получаем текущие выбранные ответы для вопроса
                selected_answers = await get_selected_answers(user_id, course_id, question_id)

                # Получаем информацию о том, является ли вопрос множественным выбором
                question = await sync_to_async(TopicQuestion.objects.get)(id=question_id)
                is_multiple_choice = question.is_multiple_choice

                if is_multiple_choice:
                    # Для множественного выбора добавляем или удаляем ответы
                    if answer_id in selected_answers:
                        selected_answers.remove(answer_id)
                    else:
                        selected_answers.append(answer_id)
                else:
                    # Для одиночного выбора заменяем ответ
                    selected_answers = [answer_id]

                # Сохранение выбранного ответа
                await save_user_answer(
                    user_id,
                    answer_id,
                    question_id,
                    course_id,
                )

                kb, sub_content = await get_questions(
                    course_id,
                    question_id,
                    callback_data.get("next_question"),
                    user_id,
                    selected_answers,
                )

            case "next_question":
                next_question = int(callback_data.get("next_question"))

                # Получаем список всех вопросов
                questions = await sync_to_async(list)(
                    TopicQuestion.objects.filter(
                        training__id=course_id, is_actual=True
                    ).order_by("id")
                )

                if next_question >= len(questions):
                    return

                # Получаем следующий вопрос и его ID
                next_question_obj = questions[next_question]
                next_question_id = str(next_question_obj.id)

                # Получаем выбранные ответы для следующего вопроса
                selected_answers = await get_selected_answers(user_id, course_id, next_question_id)

                kb, sub_content = await get_questions(
                    course_id,
                    next_question_id,
                    next_question,
                    user_id,
                    selected_answers,
                )

            case "finish_test":
                user_test = await sync_to_async(UserTest.objects.get)(
                    user__user_id=callback.from_user.id,
                    training__id=callback_data.get("course_id"),
                )
                current_user_answer = user_test.user_answer

                # Получаем все вопросы для данного курса
                all_questions = await sync_to_async(list)(
                    TopicQuestion.objects.filter(
                        training__id=callback_data.get("course_id")
                    ).values_list("id", flat=True)
                )
                all_questions = list(map(str, all_questions))

                # Проверяем, на все ли вопросы есть ответы, если нет - добавляем с is_correct = False
                for question_id in all_questions:
                    if not any(
                        result["question_id"] == question_id
                        for result in current_user_answer["results"]
                    ):
                        current_user_answer["results"].append(
                            {
                                "question_id": question_id,
                                "answer_id": [],
                                "is_correct": False,
                            }
                        )

                user_test.user_answer = current_user_answer
                await sync_to_async(user_test.save)()                
                
                # Подсчет результатов
                sub_content = await counting_correct_answers(
                    callback.from_user.id, callback_data.get("course_id")
                )
                await callback.message.delete()  # Удаляем сообщение с последним вопросом

                # Определение, пройден ли тест
                test_passed = "Поздравляю, вы успешно сдали тест" in sub_content

                # Загрузка соответствующего изображения
                result_image_path = await load_test_result_image(
                    callback.from_user.id, test_passed
                )
                media = (
                    types.InputFile(result_image_path) if result_image_path else None
                )

                # Создаем клавиатуру с кнопкой "Назад"
                kb = types.InlineKeyboardMarkup()
                kb.add(
                    types.InlineKeyboardButton(
                        text="← Назад",
                        callback_data=topic_menu.new(
                            info='topic',
                            course_id=callback_data.get("course_id"),
                            topic_id='-',
                            subtopic_id='-',
                            page=0
                        )
                    )
                )

                # Отправка результата с изображением и клавиатурой
                if media:
                    await callback.message.answer_photo(
                        photo=media, caption=sub_content, reply_markup=kb
                    )
                else:
                    await callback.message.answer(sub_content, reply_markup=kb)

                return  # Предотвращаем дальнейшее выполнение

        if kb:
            content = ""
            if media:
                photo = types.InputMediaPhoto(
                    media, caption=f"{content}\n{sub_content}"
                )
                await callback.message.edit_media(media=photo, reply_markup=kb)
            else:
                await callback.message.edit_caption(caption=f"{content}\n{sub_content}", reply_markup=kb)
        else:
            if sub_content and callback_data.get("info") != "finish_test":
                await callback.message.answer(sub_content)

    except Exception as e:
        print(e)


@dp.callback_query_handler(topic_menu.filter())
async def topic_menu_handler(callback: CallbackQuery, callback_data: dict):
    try:
        kb = None
        sub_content = ""
        image_course = None
        image_topic = None

        page = int(callback_data.get("page", 0))

        telegram_user_id = callback.from_user.id

        try:
            user = await sync_to_async(TelegramUser.objects.get)(
                user_id=telegram_user_id
            )
            internal_user_id = user.id
        except TelegramUser.DoesNotExist:
            await callback.answer("User not found in the database.", show_alert=True)
            return

        match callback_data.get("info"):
            case "in_subtopic":
                kb, sub_content, image_topic = await subtopic_menu_kb_generator(
                    callback_data.get("course_id"),
                    callback_data.get("topic_id"),
                    internal_user_id,
                    page,
                )
            case "subtopic":
                kb, sub_content, image_topic = await subtopic_menu_kb_generator(
                    callback_data.get("course_id"),
                    callback_data.get("topic_id"),
                    internal_user_id,
                    page,
                )
            case "topic":
                kb, sub_content, image_course = await topic_menu_kb_generator(
                    callback_data.get("course_id"), internal_user_id, page
                )

                # Добавляем логику записи в UserRead при нажатии на тему курса
                topic_id = callback_data.get("topic_id")
                if topic_id != "-":
                    user_read, created = await sync_to_async(
                        UserRead.objects.get_or_create
                    )(
                        user=user,
                        course_id=callback_data.get("course_id"),
                        topic_id=topic_id,
                        defaults={"is_read": True},
                    )
                    if created:
                        print("Created new UserRead record")
                    else:
                        user_read.is_read = True
                        await sync_to_async(user_read.save)()

            case "course":
                kb = await course_menu_kb_generator(user)

        # Удаляем неподдерживаемые HTML теги только из sub_content страниц
        sub_content = remove_unsupported_html_tags(sub_content)

        # Проверяем наличие изображений и обновляем сообщение
        if image_topic:
            with open(f"media/{image_topic}", "rb") as file:
                photo = types.InputMediaPhoto(file, caption=sub_content)
                await callback.message.edit_media(media=photo, reply_markup=kb)
                file.close()
        elif image_course:
            with open(f"media/{image_course}", "rb") as file:
                photo = types.InputMediaPhoto(file, caption=sub_content)
                await callback.message.edit_media(media=photo, reply_markup=kb)
                file.close()
        else:
            # Если изображений нет, загружаем логотип бота и отправляем сообщение
            title, content, photo = await load_bot_logo("tag", callback.from_user.id)
            # kb.add(types.InlineKeyboardButton(text=_('btn_close'),
            #                                   callback_data='btn_done'))

            with open(f"media/{photo}", "rb") as file:
                photo = types.InputMediaPhoto(file, caption=f"{content}\n{sub_content}")
                await callback.message.edit_media(media=photo, reply_markup=kb)
                file.close()
    except Exception as e:
        print(e)


@dp.callback_query_handler(content_selection.filter())
async def content_selection_handler(callback: CallbackQuery, callback_data: dict):
    try:
        # Если action == 'ignore', просто ответим на callback и не изменяем сообщение
        if callback_data.get("action") == "ignore":
            await callback.answer()  # Пустой ответ на callback, без изменений
            return

        page = int(callback_data.get("page", 0))
        course_id = callback_data.get("course_id")
        topic_id = callback_data.get("topic_id")
        telegram_user_id = callback.from_user.id

        kb = None
        sub_content = ""
        image_topic = None

        # Получаем объект пользователя по Telegram ID
        user = await sync_to_async(TelegramUser.objects.get)(user_id=telegram_user_id)
        internal_user_id = user.id

        # Генерируем клавиатуру и контент в зависимости от действия
        match callback_data.get("action"):
            case "select_content":
                kb, sub_content, image_topic = await subtopic_menu_kb_generator(
                    course_id, topic_id, internal_user_id, page
                )
            case "content":
                kb, sub_content, image_topic = await content_menu_kb_generator(
                    course_id, topic_id, page
                )

                # Обновляем или создаем запись в UserRead при нажатии на кнопку "Содержание темы"
                user_read, created = await sync_to_async(
                    UserRead.objects.get_or_create
                )(
                    user=user,
                    course_id=course_id,
                    topic_id=topic_id,
                    defaults={"is_read": True},
                )
                if created:
                    print("Created new UserRead record")
                else:
                    user_read.is_read = True
                    await sync_to_async(user_read.save)()

                # Проверяем, что запись обновлена
                updated_user_read = await sync_to_async(UserRead.objects.get)(
                    user=user, course_id=course_id, topic_id=topic_id
                )

        # Удаляем неподдерживаемые HTML теги только из sub_content страниц
        sub_content = remove_unsupported_html_tags(sub_content)

        if image_topic:
            with open(f"media/{image_topic}", "rb") as file:
                photo = types.InputMediaPhoto(file, caption=sub_content)
                await callback.message.edit_media(media=photo, reply_markup=kb)
                file.close()
        else:
            await callback.message.edit_reply_markup(reply_markup=kb)
            await callback.message.answer(sub_content)

    except Exception as e:
        print(f"Error in content_selection_handler: {e}")


@dp.callback_query_handler(pdf_callback.filter())
async def pdf_button_handler(callback: types.CallbackQuery, callback_data: dict):
    try:
        course_id = callback_data.get("course_id")
        topic_id = callback_data.get("topic_id")
        if not course_id or not topic_id:
            await callback.answer("Неверные данные", show_alert=True)
            return

        # Получаем объект CourseTopic
        CourseTopic = apps.get_model('educational_module', 'CourseTopic')
        topic = await sync_to_async(CourseTopic.objects.get)(id=topic_id)

        # Если PDF не задан в поле pdf_file, сообщаем об этом
        if not topic.pdf_file:
            await callback.answer("PDF не указан", show_alert=True)
            return

        # Получаем абсолютный путь к файлу
        pdf_path = topic.pdf_file.path
        if not os.path.exists(pdf_path):
            await callback.answer("Файл не найден", show_alert=True)
            return

        # Генерируем клавиатуру "назад" через subtopic_menu_kb_generator
        from app.bot.management.commands.bot_logic.kb.kb import subtopic_menu_kb_generator
        internal_user_id = callback.from_user.id  # используем id пользователя
        kb_back, _, _ = await subtopic_menu_kb_generator(course_id, topic_id, internal_user_id, page=0)

        # Если исходное сообщение уже содержит изображение – удаляем его, так как изменить его тип нельзя
        try:
            await callback.message.delete()
        except Exception as e_del:
            print("Ошибка при удалении исходного сообщения:", e_del)

        # Отправляем PDF как документ с прикрепленной клавиатурой
        with open(pdf_path, "rb") as pdf_file:
            await callback.message.answer_document(
                document=pdf_file,
                caption="PDF документ",
                reply_markup=kb_back
            )
        await callback.answer("PDF открыт", show_alert=False)
    except Exception as e:
        print("Exception in pdf_button_handler:", e)
        await callback.answer(f"Ошибка: {e}", show_alert=True)


@dp.callback_query_handler(audio_callback.filter())
async def audio_button_handler(callback: types.CallbackQuery, callback_data: dict):
    try:
        course_id = callback_data.get("course_id")
        topic_id = callback_data.get("topic_id")
        if not course_id or not topic_id:
            await callback.answer("Неверные данные", show_alert=True)
            return

        # Получаем объект CourseTopic
        CourseTopic = apps.get_model('educational_module', 'CourseTopic')
        topic = await sync_to_async(CourseTopic.objects.get)(id=topic_id)

        # Если аудио не задано в поле audio_file, сообщаем об этом
        if not topic.audio_file:
            await callback.answer("Аудио не указано", show_alert=True)
            return
        
        # Получаем абсолютный путь к файлу
        audio_path = topic.audio_file.path
        if not os.path.exists(audio_path):
            await callback.answer("Файл не найден", show_alert=True)
            return
        
        # Генерируем клавиатуру "назад" через subtopic_menu_kb_generator
        from app.bot.management.commands.bot_logic.kb.kb import subtopic_menu_kb_generator
        internal_user_id = callback.from_user.id  # используем id пользователя
        kb_back, _, _ = await subtopic_menu_kb_generator(course_id, topic_id, internal_user_id, page=0)

        # Если исходное сообщение уже содержит изображение – удаляем его, так как изменить его тип нельзя
        try:
            await callback.message.delete()
        except Exception as e_del:
            print("Ошибка при удалении исходного сообщения:", e_del)

        # Отправляем аудио как документ с прикрепленной клавиатурой
        with open(audio_path, "rb") as audio_file:
            await callback.message.answer_document(
                document=audio_file,
                caption="Аудио файл",
                reply_markup=kb_back
            )
        await callback.answer("Аудио файл открыт", show_alert=False)
    except Exception as e:
        print("Exception in audio_button_handler:", e)
        await callback.answer(f"Ошибка: {e}", show_alert=True)


@dp.callback_query_handler(video_callback.filter())
async def video_button_handler(callback: types.CallbackQuery, callback_data: dict):
    try:
        course_id = callback_data.get("course_id")
        topic_id = callback_data.get("topic_id")
        if not course_id or not topic_id:
            await callback.answer("Неверные данные", show_alert=True)
            return

        # Получаем объект CourseTopic
        CourseTopic = apps.get_model('educational_module', 'CourseTopic')
        topic = await sync_to_async(CourseTopic.objects.get)(id=topic_id)

        # Если аудио не задано в поле audio_file, сообщаем об этом
        if not topic.video_file:
            await callback.answer("Видео не указано", show_alert=True)
            return
        
        # Получаем абсолютный путь к файлу
        video_path = topic.video_file.path
        if not os.path.exists(video_path):
            await callback.answer("Файл не найден", show_alert=True)
            return
        
        # Генерируем клавиатуру "назад" через subtopic_menu_kb_generator
        from app.bot.management.commands.bot_logic.kb.kb import subtopic_menu_kb_generator
        internal_user_id = callback.from_user.id  # используем id пользователя
        kb_back, _, _ = await subtopic_menu_kb_generator(course_id, topic_id, internal_user_id, page=0)

        # Если исходное сообщение уже содержит изображение – удаляем его, так как изменить его тип нельзя
        try:
            await callback.message.delete()
        except Exception as e_del:
            print("Ошибка при удалении исходного сообщения:", e_del)

        # Отправляем аудио как документ с прикрепленной клавиатурой
        with open(video_path, "rb") as video_file:
            await callback.message.answer_document(
                document=video_file,
                caption="Видео файл",
                reply_markup=kb_back
            )
        await callback.answer("Видео файл открыт", show_alert=False)
    except Exception as e:
        print("Exception in audio_button_handler:", e)
        await callback.answer(f"Ошибка: {e}", show_alert=True)
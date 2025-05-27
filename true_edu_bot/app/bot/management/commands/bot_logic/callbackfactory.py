from aiogram.utils.callback_data import CallbackData


topic_menu = CallbackData('topic_menu', 'info', 'course_id', 'topic_id', 'subtopic_id', 'page')
begin_test = CallbackData('begin_test', "info", "course_id", "question_id", "next_question", "answer_id")
content_selection = CallbackData('content_selection', 'action', 'course_id', 'topic_id', 'page')

set_address_settings = CallbackData('set_address_settings', 'state_info')

test_menu = CallbackData('test_menu', 'info', 'course_id', 'topic_id', 'question_id', 'current_question_index',
                         'answer_id')

pdf_callback = CallbackData("pdf", "course_id", "topic_id")
audio_callback = CallbackData("audio", "course_id", "topic_id")
video_callback = CallbackData("video", "course_id", "topic_id")
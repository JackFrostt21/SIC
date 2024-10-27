import os
from aiogram import types
from aiogram.types import WebAppInfo


from app.bot.management.commands.bot_logic.functions import user_get_tools
from app.bot.management.commands.bot_logic.handlers.callbackhandlers.educational_logic import course_menu_kb_generator
from app.bot.management.commands.bot_logic.handlers.callbackhandlers.progress_logic import progress_result
from app.bot.management.commands.bot_logic.handlers.callbackhandlers.settings_logics import kb_settings
# from app.bot.management.commands.bot_logic.kb.test_kb import training_course_menu_kb_generator
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.loader import dp, bot

i18n = setup_middleware(dp)
_ = i18n.gettext


@dp.message_handler(content_types=types.ContentType.ANY)
async def main_menu(message: types.Message):
    user = await user_get_tools(message.from_user.id)
    # bot_info_url = "http://127.0.0.1:8000/api/testing-testing_module/bot-info/"
    try:
        if message.text == _('self-study'):
            user = await user_get_tools(message.from_user.id)
            if user.testing_process:
                await message.answer(_('The training manual is not available while testing is in progress.'))
            else:
                kb = await course_menu_kb_generator(user)
                image_path = user.company.image_list_courses.path
                if os.path.exists(image_path):
                    media = types.InputFile(image_path)
                    await message.answer_photo(photo=media,
                                               caption=_('Список ваших курсов'),
                                               parse_mode='HTML',
                                               reply_markup=kb)
                else:
                    await message.answer(_('Список ваших курсов'),
                                        parse_mode='HTML',
                                        reply_markup=kb)

                    
        # if message.text == 'О боте':
        #     await message.answer(bot_info_url)
        
        # if _('self-progress') in message.text:
        #     res = await progress_result(user_id=message.from_user.id)
        #     image_path = user.company.image_progress.path
        #     if os.path.exists(image_path):
        #         media = types.InputFile(image_path)
        #         await message.answer_photo(photo=media,
        #                                    caption=res,
        #                                    parse_mode='HTML')
        #     else:
        #         await message.answer(text=res)

        if message.text == _('Settings'):
            kb = kb_settings((await user_get_tools(message.from_user.id)).language)
            image_path = user.company.image_list_settings.path
            if os.path.exists(image_path):
                media = types.InputFile(image_path)
                await message.answer_photo(photo=media,
                                           caption=_('Выберите язык:'),
                                           parse_mode='HTML',
                                           reply_markup=kb.add(
                                               types.InlineKeyboardButton(text=_('btn_close'),
                                                                          callback_data='btn_done')
                                           ))
            else:
                await message.answer(text='content',
                                     parse_mode='HTML',
                                     reply_markup=kb.add(
                                         types.InlineKeyboardButton(text=_('btn_close'),
                                                                    callback_data='btn_done')
                                     ))
        menu_list = [_('self-study'), _('testing'), _('Settings'), 'О боте']
        if message.text not in menu_list and not _('self-progress') in message.text and not message.via_bot:
            await bot.send_message(message.from_user.id, message.text)
            await message.answer(text=f'❌!Error!❌ \nCommand not found. Press -> /start')
    except Exception as e:
        print(e)
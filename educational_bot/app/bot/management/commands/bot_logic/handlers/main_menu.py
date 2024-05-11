from aiogram import types
from aiogram.types import WebAppInfo

from app.bot.management.commands.bot_logic.functions import user_get_tools
from app.bot.management.commands.bot_logic.handlers.callbackhandlers.educational_logic import course_menu_kb_generator
from app.bot.management.commands.bot_logic.handlers.callbackhandlers.progress_logic import progress_result
from app.bot.management.commands.bot_logic.handlers.callbackhandlers.settings_logics import kb_settings
from app.bot.management.commands.bot_logic.handlers.callbackhandlers.testing_logic import \
    training_course_menu_kb_generator
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.loader import dp, bot

i18n = setup_middleware(dp)
_ = i18n.gettext


@dp.message_handler(content_types=types.ContentType.ANY)
async def main_menu(message: types.Message):
    user = await user_get_tools(message.from_user.id)
    try:
        if message.text == _('self-study'):
            user = await user_get_tools(message.from_user.id)
            if user.testing_process:
                await message.answer(_('The training manual is not available while testing is in progress.'))
            else:
                kb = await course_menu_kb_generator()
                kb.add(types.InlineKeyboardButton(text=_('📓 База Знаний 📔'),
                                                  web_app=WebAppInfo(url='https://nickbarb.github.io/my_test_tg/')))
                media = types.InputFile(f'media/settings/logo-ngs-all.png')
                await message.answer_photo(photo=media,
                                           caption='content',
                                           parse_mode='HTML',
                                           reply_markup=kb.add(
                                               types.InlineKeyboardButton(text=_('btn_close'),
                                                                          callback_data='btn_done')
                                           ))

        if message.text == _('testing'):
            if not user.testing_process:

                kb, content = await training_course_menu_kb_generator(message.from_user.id)
                media = types.InputFile(f'media/settings/logo-ngs-all.png')
                await message.answer_photo(
                    photo=media,
                    caption=f"📚📝{content}",
                    parse_mode='HTML',
                    reply_markup=kb)
            else:
                await message.answer(_("You're already on the test"))

        if _('self-progress') in message.text:
            res = await progress_result(user_id=message.from_user.id)
            await message.answer(text=res)
        if message.text == _('Settings'):
            kb = kb_settings((await user_get_tools(message.from_user.id)).language)
            media = types.InputFile(f'media/settings/logo-ngs-all.png')
            await message.answer_photo(photo=media,
                                       caption='content',
                                       parse_mode='HTML',
                                       reply_markup=kb.add(
                                           types.InlineKeyboardButton(text=_('btn_close'),
                                                                      callback_data='btn_done')
                                       ))
        menu_list = [_('self-study'), _('testing'), _('Settings')]
        if message.text not in menu_list and not _('self-progress') in message.text and not message.via_bot:
            await bot.send_message(message.from_user.id, message.text)
            await message.answer(text=f'❌!Error!❌ \nCommand not found. Press -> /start')
    except Exception as e:
        print(e)

from aiogram import types
from aiogram.utils.callback_data import CallbackData
from app.bot.management.commands.loader import dp
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.bot_logic.functions import user_get_tools, user_set_language, load_bot_logo
from app.bot.management.commands.bot_logic.callbackfactory import set_address_settings

i18n = setup_middleware(dp)
_ = i18n.gettext


def kb_settings(language):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    match language:
        case 'ru':
            kb.add(types.InlineKeyboardButton(text='☑️ ' + '🇷🇺', callback_data='settings_set ru'),
                   types.InlineKeyboardButton(text='✔️ ' + "🇺🇿", callback_data='settings_set uz'),
                   types.InlineKeyboardButton(text='✔️ ' + '🇬🇧', callback_data='settings_set en'))
        case 'uz':
            kb.add(types.InlineKeyboardButton(text='✔️ ' + '🇷🇺', callback_data='settings_set ru'),
                   types.InlineKeyboardButton(text='☑️ ' + "🇺🇿", callback_data='settings_set uz'),
                   types.InlineKeyboardButton(text='✔️ ' + '🇬🇧', callback_data='settings_set en'))
        case 'en':
            kb.add(types.InlineKeyboardButton(text='✔️ ' + '🇷🇺', callback_data='settings_set ru'),
                   types.InlineKeyboardButton(text='✔️ ' + "🇺🇿", callback_data='settings_set uz'),
                   types.InlineKeyboardButton(text='☑️ ' + '🇬🇧', callback_data='settings_set en'))
    return kb


@dp.callback_query_handler(text_contains='settings_set')
async def settings_set(callback: types.CallbackQuery):
    try:
        user_set_options = callback.data[13:]
        if user_set_options in ['ru', 'uz', 'en']:
            await user_set_language(callback.from_user.id, user_set_options)

        # user = await user_get_tools(callback.from_user.id)
        kb = kb_settings((await user_get_tools(callback.from_user.id)).language)
        title, content, photo = await load_bot_logo('tag', callback.from_user.id)
        if len(callback.data) > 12:
            with open(f'media/{photo}', 'rb') as file:
                photo = types.InputMediaPhoto(file, caption=content)
                await callback.message.edit_media(media=photo, reply_markup=kb.add(
                    types.InlineKeyboardButton(text=_('done'),
                                               callback_data='btn_done')))
        else:
            with open(f'media/{photo}', 'rb') as file:
                photo = types.InputMediaPhoto(file, caption=content)
                await callback.message.edit_media(media=photo, reply_markup=kb.add(
                    types.InlineKeyboardButton(text=_('btn_close'),
                                               callback_data='btn_done')
                ))
    except Exception as e:
        print(e)




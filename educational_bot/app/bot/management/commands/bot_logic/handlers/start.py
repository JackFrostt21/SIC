from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, CallbackQuery
from asgiref.sync import sync_to_async
from icecream import ic

from typing import Union #add for cmd_start(message: Union[types.Message, types.CallbackQuery])

from app.bot.management.commands.bot_logic.functions import user_exists, load_bot_logo, user_change_test_status
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.bot_logic.states import LocaleRegSteps
from app.bot.management.commands.loader import dp
from app.educational_module.models import TopicQuestion, CourseTopic, TrainingCourse
from .callbackhandlers.testing_logic import training_course_menu_kb_generator

i18n = setup_middleware(dp)
_ = i18n.gettext

'''------------------------------------------------Functions------------------------------------------------'''


@sync_to_async
def building_main_menu(user_id):
    menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    item_count = len(TrainingCourse.objects.filter(user__user_id=user_id))
    if item_count > 0:
        item_count = f'{item_count}'
    else:
        item_count = f''
    (menu_keyboard
     .row(KeyboardButton(_('self-study')))  # , web_app=WebAppInfo(url='https://nickbarb.github.io/my_test_tg/')
     .row(KeyboardButton(_('testing')))
     .row(KeyboardButton(_('self-progress') + f' ({item_count})'), KeyboardButton(_('Settings'))))
    return menu_keyboard


'''------------------------------------------------Start------------------------------------------------'''


async def soft_state_finish(state: FSMContext):
    fields = ['action', 'Yes_No']
    data = await state.get_data()
    data = {key: value for key, value in data.items() if key not in fields}
    await state.set_data(data)
    await state.set_state(None)


@dp.message_handler(commands=['Start'], state="*")
async def cmd_start(message: Union[types.Message, types.CallbackQuery]): #add Union
    try:

        match await user_exists(message.from_user.id, message.from_user.full_name, message.from_user.mention):
            case 1:
                title, content, photo = await load_bot_logo('main_menu_logo', message.from_user.id)
                menu_keyboard = await building_main_menu(message.from_user.id)
                media = types.InputFile(f'media/{photo}')
                await message.answer_photo(photo=media,
                                           caption=f'<code>{title}\n'
                                                   f'{content}\n</code>'
                                                   f'<i>{message.from_user.full_name}</i>\n'
                                                   f' <b>{message.from_user.mention}</b>',
                                           reply_markup=menu_keyboard)
            case 0:
                title, content, photo = await load_bot_logo('welcome_logo', message.from_user.id)
                media = types.InputFile(f'media/{photo}')
                await message.answer_photo(photo=media,
                                           caption=f'<code>{title}\n'
                                                   f'{content}\n</code>'
                                                   f'<i>{message.from_user.full_name}</i>\n'
                                                   f' <b>{message.from_user.mention}</b>',
                                           reply_markup=types.ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton('🇷🇺Русский'),
                                                KeyboardButton("🇺🇿O'zbek"),
                                                KeyboardButton('🇬🇧English')
                                                ]
                                           ],
                                               resize_keyboard=True
                                           ), )
                await LocaleRegSteps.set_language.set()
            case 2:
                title, content, photo = await load_bot_logo('user_blocked_logo', message.from_user.id)
                content = _('The module will be available after the Administrator checks.')
                media = types.InputFile(f'media/{photo}')
                await message.answer_photo(photo=media,
                                           caption=f'<code>{title}\n'
                                                   f'{content}\n</code>'
                                                   f'<i>{message.from_user.full_name}</i>\n'
                                                   f' <b>{message.from_user.mention}</b>',
                                           reply_markup=types.ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton('/start')]
                                           ],
                                               resize_keyboard=True
                                           ), )

    except Exception as e:
        print(e)


''' -ИМПОРТ- -Callback Handlers-'''
from . import callbackhandlers

ic(callbackhandlers)

'''------------------------------------------------BasemenT------------------------------------------------'''


@dp.callback_query_handler(text_contains='btn_done')
async def settings_set_done(call: CallbackQuery):
    try:
        # menu_keyboard = await building_main_menu(call.from_user.id)
        await call.message.delete_reply_markup()
        await call.message.delete()
        # await bot.send_message(chat_id=call.from_user.id, text=_('Main menu'), reply_markup=menu_keyboard)
        match await user_exists(call.from_user.id, call.from_user.full_name, call.from_user.mention):
            case 1:
                title, content, photo = await load_bot_logo('main_menu_logo', call.from_user.id)
                menu_keyboard = await building_main_menu(call.from_user.id)
                media = types.InputFile(f'media/{photo}')
                await call.message.answer_photo(photo=media,
                                                caption=f'<code>{title}\n'
                                                        f'{content}\n</code>'
                                                        f'<i>{call.from_user.full_name}</i>\n'
                                                        f' <b>{call.from_user.mention}</b>',
                                                reply_markup=menu_keyboard)
            case 0:
                title, content, photo = await load_bot_logo('welcome_logo', call.from_user.id)
                media = types.InputFile(f'media/{photo}')
                await call.message.answer_photo(photo=media,
                                                caption=f'<code>{title}\n'
                                                        f'{content}\n</code>'
                                                        f'<i>{call.from_user.full_name}</i>\n'
                                                        f' <b>{call.from_user.mention}</b>',
                                                reply_markup=types.ReplyKeyboardMarkup(keyboard=[
                                                    [KeyboardButton('🇷🇺Русский'),
                                                     KeyboardButton("🇺🇿O'zbek"),
                                                     KeyboardButton('🇬🇧English')
                                                     ]
                                                ],
                                                    resize_keyboard=True
                                                ), )
                await LocaleRegSteps.set_language.set()
            case 2:
                title, content, photo = await load_bot_logo('user_blocked_logo', call.from_user.id)
                content = _('The module will be available after the Administrator checks.')
                media = types.InputFile(f'media/{photo}')
                await call.message.answer_photo(photo=media,
                                                caption=f'<code>{title}\n'
                                                        f'{content}\n</code>'
                                                        f'<i>{call.from_user.full_name}</i>\n'
                                                        f' <b>{call.from_user.mention}</b>',
                                                reply_markup=types.ReplyKeyboardMarkup(keyboard=[
                                                    [KeyboardButton('/start')]
                                                ],
                                                    resize_keyboard=True
                                                ), )
    except Exception as e:
        print(e)


@dp.callback_query_handler(state='*')
async def any_callback(callback: types.CallbackQuery):
    print('FATAL ERROR - No one callback handler!')
    await callback.message.edit_reply_markup(InlineKeyboardMarkup())

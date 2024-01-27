from aiogram import Router, types, F, filters
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(F.text)
async def main_menu(message: types.Message):
    if message.text == "main_menu":
        kb_builder = InlineKeyboardBuilder()
        kb_builder.row(
            types.InlineKeyboardButton(text="data", callback_data="data"),
            types.InlineKeyboardButton(text="data_2", callback_data="data_2")
        )
        kb_builder.add(types.InlineKeyboardButton(
            text="data",
            callback_data="data")
        )
        kb_builder.add(types.InlineKeyboardButton(
            text="data_2",
            callback_data="data_2")
        )
        kb_builder.adjust(2, 1, 1)
        await message.answer(text="main_menu", reply_markup=kb_builder.as_markup())
    else:
        await message.answer(text=message.text)

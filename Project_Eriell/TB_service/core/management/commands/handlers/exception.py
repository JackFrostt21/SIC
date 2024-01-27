from aiogram import Router, types

router = Router()


@router.callback_query()
async def any_callback(callback: types.CallbackQuery):
    print('FATAL ERROR - No one callback handler!')
    await callback.answer(text='FATAL ERROR - No one callback handler!',
                          show_alert=True)

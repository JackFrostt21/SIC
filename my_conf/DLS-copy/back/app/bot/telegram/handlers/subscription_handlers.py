"""
Обработчики для управления подписками на уведомления о новых курсах
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async

from app.bot.telegram.keyboards.subscription_kb import get_subscription_keyboard
from app.bot.telegram.callback.schemas import SubscriptionCallback
from app.bot.models.telegram_user import TelegramUser, SubscriptionUser

# Создаем роутер для обработчиков подписок
router = Router(name="subscription_router")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


@router.message(F.text == "🔔 Уведомления о новых курсах")
async def process_subscription_menu(message: Message) -> None:
    """
    Обрабатывает нажатие на кнопку "Уведомления о новых курсах"
    Отображает меню управления подписками с инлайн-кнопками
    """
    logger.info(f"User {message.from_user.id} opened subscription menu")

    telegram_id = message.from_user.id

    # Проверяем текущий статус подписки
    is_subscribed = await sync_to_async(
        lambda: SubscriptionUser.objects.filter(telegram_id=telegram_id).exists()
    )()

    # Формируем текст сообщения в зависимости от статуса подписки
    if is_subscribed:
        message_text = (
            "<b>🔔 Управление уведомлениями</b>\n\n"
            "✅ Вы подписаны на уведомления о новых курсах!\n\n"
            "Вы будете получать сообщения о появлении новых программ обучения.\n"
            "Чтобы отключить уведомления, нажмите кнопку ниже."
        )
    else:
        message_text = (
            "<b>🔔 Управление уведомлениями</b>\n\n"
            "🔕 Уведомления отключены.\n\n"
            "Включите уведомления, чтобы первыми узнавать о новых программах обучения!\n"
            "Вы будете получать сообщения о появлении интересных курсов."
        )

    # Получаем клавиатуру
    keyboard = await get_subscription_keyboard()

    # Отправляем сообщение с инлайн-кнопками
    await message.answer(text=message_text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(SubscriptionCallback.filter(F.action == "enable"))
async def process_enable_subscription(
    callback: CallbackQuery, callback_data: SubscriptionCallback
) -> None:
    """
    Обрабатывает включение подписки на уведомления
    Создает или обновляет запись в SubscriptionUser
    """
    logger.info(f"User {callback.from_user.id} enabling subscription")
    await callback.answer()

    telegram_id = callback.from_user.id

    try:
        # Получаем пользователя
        telegram_user = await sync_to_async(TelegramUser.objects.get)(
            telegram_id=telegram_id
        )

        # Проверяем, существует ли уже подписка
        subscription_exists = await sync_to_async(
            lambda: SubscriptionUser.objects.filter(telegram_id=telegram_id).exists()
        )()

        if subscription_exists:
            # Подписка уже существует
            success_message = (
                "✅ <b>Уведомления уже включены!</b>\n\n"
                "Вы уже подписаны на получение уведомлений о новых курсах. "
                "Мы оповестим вас, как только появятся новые программы обучения!"
            )
            logger.info(f"User {telegram_id} already has an active subscription")
        else:
            # Создаем новую подписку
            await sync_to_async(SubscriptionUser.objects.create)(
                user=telegram_user, telegram_id=telegram_id
            )
            success_message = (
                "🎉 <b>Уведомления успешно включены!</b>\n\n"
                "Отлично! Теперь вы будете получать уведомления о новых курсах. "
                "Мы сообщим вам о появлении интересных программ обучения. "
                "Вы можете отключить уведомления в любой момент."
            )
            logger.info(f"Successfully created subscription for user {telegram_id}")

        # Обновляем сообщение
        await callback.message.edit_text(text=success_message, parse_mode="HTML")

    except TelegramUser.DoesNotExist:
        logger.error(f"TelegramUser not found for telegram_id: {telegram_id}")
        await callback.answer(
            "❌ Ошибка: пользователь не найден. Пожалуйста, пройдите регистрацию.",
            show_alert=True,
        )
    except Exception as e:
        logger.error(f"Error enabling subscription for user {telegram_id}: {e}")
        await callback.answer(
            f"❌ Произошла ошибка при включении уведомлений: {e}", show_alert=True
        )


@router.callback_query(SubscriptionCallback.filter(F.action == "disable"))
async def process_disable_subscription(
    callback: CallbackQuery, callback_data: SubscriptionCallback
) -> None:
    """
    Обрабатывает отключение подписки на уведомления
    Удаляет запись из SubscriptionUser, если она существует
    """
    logger.info(f"User {callback.from_user.id} disabling subscription")
    await callback.answer()

    telegram_id = callback.from_user.id

    try:
        # Пытаемся найти и удалить подписку
        subscription = await sync_to_async(
            lambda: SubscriptionUser.objects.filter(telegram_id=telegram_id).first()
        )()

        if subscription:
            # Удаляем подписку
            await sync_to_async(subscription.delete)()
            success_message = (
                "🔕 <b>Уведомления отключены</b>\n\n"
                "Вы успешно отписались от уведомлений о новых курсах. "
                "Вы больше не будете получать автоматические сообщения. "
                "При желании вы можете снова включить уведомления в любой момент."
            )
            logger.info(f"Successfully deleted subscription for user {telegram_id}")
        else:
            # Подписка не найдена
            success_message = (
                "ℹ️ <b>Уведомления уже отключены</b>\n\n"
                "У вас нет активной подписки на уведомления о новых курсах. "
                "Если вы хотите получать информацию о новых программах обучения, "
                "вы можете включить уведомления."
            )
            logger.info(f"No subscription found for user {telegram_id}")

        # Обновляем сообщение
        await callback.message.edit_text(text=success_message, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error disabling subscription for user {telegram_id}: {e}")
        await callback.answer(
            f"❌ Произошла ошибка при отключении уведомлений: {e}", show_alert=True
        )

import logging
from aiogram import F, Router
from aiogram.types import CallbackQuery

from sisu_bot.bot.formatters.user_formatters import format_my_rank, format_top_users
from sisu_bot.bot.handlers.checkin_handler import handle_checkin_command
from sisu_bot.bot.handlers.donate_handler import handle_donate_command_new
from sisu_bot.bot.handlers.ref_handler import handle_ref_command
from sisu_bot.bot.services import points_service, top_service

router = Router()


async def handle_myrank_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        position_tuple = top_service.get_user_position(user_id)
        if not position_tuple:
            await callback.message.answer("Не нашел вас в базе. Начните общаться, чтобы появиться в топе!")
            return

        with points_service.session_scope() as session:
            user = session.query(points_service.User).filter(points_service.User.id == user_id).first()
            if not user:
                await callback.message.answer("Произошла странная ошибка синхронизации. Попробуйте еще раз.")
                return

            rank_info = points_service.get_rank_info(user.id)
            global_rank = position_tuple[0]
            text = format_my_rank(user, rank_info, global_rank)
            await callback.message.answer(text, parse_mode="HTML")

    except Exception:
        logging.exception("Ошибка в handle_myrank_callback")
        await callback.message.answer("Не удалось получить информацию о ранге 😢")


async def handle_top_players_callback(callback: CallbackQuery):
    try:
        top_users = top_service.get_top_users(limit=10)
        text = format_top_users(top_users)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        logging.exception("Ошибка в handle_top_players_callback")
        await callback.message.answer("Ошибка при формировании топа 😢")


async def show_help_callback(callback: CallbackQuery):
    help_text = (
        "<b>Список доступных команд:</b>\n\n"
        "/start - Перезапустить бота\n"
        "/myrank - Узнать свой ранг и количество баллов\n"
        "/top - Показать топ-5 активных участников\n"
        "/checkin - Ежедневная отметка для получения баллов\n"
        "/ref - Получить свою реферальную ссылку\n"
        "/donate - Информация о поддержке проекта"
    )
    await callback.message.answer(help_text, parse_mode="HTML")


async def show_games_info_callback(callback: CallbackQuery):
    await callback.message.answer("Раздел 'Игры' находится в разработке.")


@router.callback_query(F.data.in_([
    "my_rank", "top_players", "checkin", "games", "donate", "referral", "help"
]))
async def handle_main_menu_callbacks(callback: CallbackQuery):
    """
    Этот обработчик теперь вызывает либо асинхронные функции, определенные
    в этом файле (которые правильно работают с сервисами), либо
    оригинальные обработчики команд, если они простые.
    """
    command_map = {
        "my_rank": handle_myrank_callback,
        "top_players": handle_top_players_callback,
        "checkin": handle_checkin_command,
        "donate": handle_donate_command_new,
        "referral": handle_ref_command,
        "help": show_help_callback,
        "games": show_games_info_callback,
    }

    handler = command_map.get(callback.data)

    if handler:
        try:
            # Для простых обработчиков, которые ожидают `Message`
            if callback.data in ["checkin", "donate", "referral"]:
                 await handler(callback.message)
            # Для новых, правильных обработчиков, которые ожидают `CallbackQuery`
            else:
                await handler(callback)
        except Exception as e:
            logging.error(f"Error handling callback {callback.data}: {e}", exc_info=True)
            await callback.message.answer("Произошла ошибка при обработке вашего запроса. Попробуйте позже.")

    await callback.answer() 
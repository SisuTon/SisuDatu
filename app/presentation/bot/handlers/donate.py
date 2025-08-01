from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, InputMediaDocument
from aiogram.filters import Command
from app.shared.config.bot_config import ADMIN_IDS
from app.shared.config.settings import DONATION_TIERS
from app.domain.services.gamification import points as points_service
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import logging

router = Router()

# TON адрес для донатов
TON_WALLET = "UQDpKfZQy_gFnsZxwE2A6FeTQUXimR9VWjnd1C_8R5Cn0hnv"

# ID группы для публичного сообщения (замени на свой)
SUPPORTER_ANNOUNCE_CHAT_ID = -1002565290281  # пример, замени на свой

# Словарь для хранения ожидающих подтверждения донатов: user_id -> (message_id, chat_id)
pending_donations = {}

BOT_USERNAME = "SisuDatuBot"  # Укажи актуальный username бота, если другой

class DonateStates(StatesGroup):
    waiting_proof = State()

def get_donate_keyboard():
    """Создает клавиатуру с кнопками для разных сумм доната через универсальный TON deeplink и копирования кошелька"""
    buttons = []
    # Кнопки для каждого уровня доната
    for tier_code, tier_info in DONATION_TIERS.items():
        amount_nano = str(int(tier_info["min_amount_ton"] * 1_000_000_000))
        url = f"ton://transfer/{TON_WALLET}?amount={amount_nano}"
        buttons.append(InlineKeyboardButton(
            text=f"💎 {tier_info['min_amount_ton']} TON - {tier_info['title']}",
            url=url
        ))
    
    # Кнопка с произвольной суммой
    buttons.append(InlineKeyboardButton(
        text="💎 Другая сумма",
        url=f"ton://transfer/{TON_WALLET}"
    ))
    # Кнопка для копирования кошелька
    copy_button = InlineKeyboardButton(
        text="📋 Скопировать TON-кошелек",
        callback_data="copy_ton_wallet"
    )
    # Кнопка 'Я задонатил!'
    confirm_button = InlineKeyboardButton(
        text="✅ Я задонатил!",
        callback_data="donate_confirm"
    )
    # Формируем клавиатуру: уровни по 1 в ряд, затем произвольная сумма, затем копировать, затем 'Я задонатил!'
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [btn] for btn in buttons
        ] + [[copy_button], [confirm_button]]
    )
    return keyboard

@router.callback_query(lambda c: c.data == "copy_ton_wallet")
async def copy_wallet_callback(call):
    await call.answer("TON-кошелек скопирован!", show_alert=True)
    await call.message.answer(f"TON-кошелек для доната: <code>{TON_WALLET}</code>", parse_mode="HTML")

@router.callback_query(lambda c: c.data == "donate_confirm")
async def donate_confirm_callback(call, state: FSMContext):
    await call.answer()
    await call.message.answer(
        "Пожалуйста, пришли хеш транзакции или скриншот перевода TON сюда одним сообщением.\n\n"
        "После проверки админом ты получишь свой статус Supporter!"
    )
    # Сохраняем user_id в состоянии для последующего подтверждения
    await state.update_data(user_id_awaiting_proof=call.from_user.id)
    await state.set_state(DonateStates.waiting_proof)

@router.message(Command("donate"))
async def donate_handler(msg: Message):
    if msg.chat.type in ("group", "supergroup"):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="💎 Донатить в личке боту",
                    url=f"https://t.me/{BOT_USERNAME}?start=donate"
                )]
            ]
        )
        await msg.answer(
            "💎 <b>Сделай Sisu Datu Bot круче — поддержи проект!</b>\n\n"
            "Нажми кнопку и поддержи проект в личке!\n\n"
            "<i>Для приватности донать только в личке с ботом!</i>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return
    keyboard = get_donate_keyboard()
    benefits_text = (
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>🔥 Варианты поддержки:</b>\n\n"
        "🥉 <b>Bronze</b> — 1 TON\n"
        "Ты в клубе избранных! Получаешь магический знак и +1000 баллов. Остальные пусть завидуют!\n\n"
        "🥈 <b>Silver</b> — 5 TON\n"
        "Становишься ближе к сердцу дракона! Ещё больше магии и +3000 баллов.\n\n"
        "🥇 <b>Gold</b> — 10 TON\n"
        "Ты — легенда! Твой ник сияет в топе, +7000 баллов и уважение всей драконьей братии.\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await msg.answer(
        "💎 <b>Сделай Sisu Datu Bot круче — поддержи проект!</b>\n\n"
        "🔗 TON-кошелек:\n"
        f"<code>{TON_WALLET}</code>\n\n"
        "📱 <i>Донать удобно через мобильный TON-кошелек!</i>\n\n"
        f"{benefits_text}\n\n"
        "🐉 После доната ты появишься в топе как <b>Донатер</b> (Воин дракона)!\n\n"
        "👇 Жми <b>Я задонатил!</b> после перевода.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(DonateStates.waiting_proof)
async def handle_donate_proof(msg: Message, state: FSMContext):
    data = await state.get_data()
    user_id_awaiting_proof = data.get("user_id_awaiting_proof")
    if not user_id_awaiting_proof:
        logging.error(f"handle_donate_proof: No user_id_awaiting_proof in state for {msg.from_user.id}")
        await msg.answer("Произошла ошибка. Пожалуйста, попробуйте начать процесс доната снова.")
        await state.clear()
        return

    # Пересылаем админу(ам) с кнопками выбора уровня доната
    keyboard_buttons = []
    for tier_code, tier_info in DONATION_TIERS.items():
        keyboard_buttons.append(InlineKeyboardButton(
            text=f"Подтвердить {tier_info['title']}",
            callback_data=f"approve_donate_{user_id_awaiting_proof}_{tier_code}"
        ))
    # Разбиваем кнопки на ряды по 2
    tier_keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_buttons[i:i + 2] for i in range(0, len(keyboard_buttons), 2)])

    for admin_id in ADMIN_IDS:
        caption_text = f"Донат от @{msg.from_user.username or msg.from_user.id}\nID: {user_id_awaiting_proof}\n\nПредполагаемый уровень: [Заполнить админу]"
        if msg.photo:
            await msg.bot.send_photo(admin_id, msg.photo[-1].file_id, caption=caption_text,
                                     reply_markup=tier_keyboard)
        elif msg.document:
            await msg.bot.send_document(admin_id, msg.document.file_id, caption=caption_text,
                                        reply_markup=tier_keyboard)
        else:
            await msg.bot.send_message(admin_id, f"{caption_text}\n\nСообщение: {msg.text}",
                                      reply_markup=tier_keyboard)
    await msg.answer("Спасибо! Сообщение отправлено админу. Ожидай подтверждения и своего статуса Supporter.")
    await state.clear()

@router.callback_query(lambda c: c.data and c.data.startswith("approve_donate_"))
async def approve_donate_tier_callback(call: CallbackQuery):
    parts = call.data.split("_")
    user_id = int(parts[2])
    tier_code = parts[3]

    if tier_code not in DONATION_TIERS:
        logging.error(f"approve_donate_tier_callback: Invalid tier_code {tier_code}")
        await call.answer("Ошибка: Неизвестный уровень доната.", show_alert=True)
        return

    tier_info = DONATION_TIERS[tier_code]
    # Фиксированные баллы за донат
    fixed_points = {"bronze": 1000, "silver": 3000, "gold": 7000}.get(tier_code, 1000)
    duration_days = tier_info["duration_days"]

    # Устанавливаем статус Supporter и баллы
    session = points_service.Session() # Используем сессию из points_service для консистентности
    user = session.query(points_service.User).filter(points_service.User.id == user_id).first()

    if not user:
        user = points_service.User(id=user_id)
        session.add(user)

    user.is_supporter = True
    user.supporter_tier = tier_code
    user.supporter_until = datetime.utcnow() + timedelta(days=duration_days)
    # Начисляем фиксированные баллы
    points_service.add_points(user_id, fixed_points)
    # Важно: ChatPoints баллы не должны зависеть от доната, это баллы за активность

    # Сохраняем данные до закрытия сессии
    supporter_until_str = user.supporter_until.strftime('%d.%m.%Y')
    username = user.username
    name = username and f"@{username}" or f"ID {user_id}"
    
    session.commit()
    session.close()

    # Уведомляем пользователя
    try:
        await call.bot.send_message(user_id, 
            f"🎉 Твой донат подтвержден!\n\n"\
            f"Ты получил статус <b>{tier_info['title']}</b> до {supporter_until_str}!\n"\
            f"Начислено {fixed_points} баллов.\n"\
            f"<b>Плюшки:</b> {', '.join(tier_info['benefits'])}"
            , parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления пользователю {user_id} о подтверждении доната: {e}", exc_info=True)

    # Публичное сообщение в группу
    try:
        await call.bot.send_message(
            SUPPORTER_ANNOUNCE_CHAT_ID,
            f"🎉 {name} поддержал проект и стал <b>{tier_info['title']}</b>!\nСпасибо за вклад в развитие Sisu Datu Bot! 🐉💎",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке публичного уведомления о донате: {e}", exc_info=True)

    await call.answer(f"Донат подтвержден для {user_id} на уровень {tier_info['title']}!", show_alert=True) 
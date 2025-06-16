from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, InputMediaDocument
from aiogram.filters import Command
from sisu_bot.bot.config import ADMIN_IDS
from sisu_bot.bot.services import points_service
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# TON адрес для донатов
TON_WALLET = "UQDpKfZQy_gFnsZxwE2A6FeTQUXimR9VWjnd1C_8R5Cn0hnv"

# Суммы в нано-TON (1 TON = 1000000000 нано-TON)
DONATE_AMOUNTS = {
    "0.5 TON": "500000000",
    "1 TON": "1000000000",
    "2 TON": "2000000000",
    "5 TON": "5000000000"
}

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
    # Кнопки с фиксированными суммами через универсальный deeplink
    for amount, nano_amount in DONATE_AMOUNTS.items():
        url = f"ton://transfer/{TON_WALLET}?amount={nano_amount}"
        buttons.append(InlineKeyboardButton(
            text=f"💎 {amount}",
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
    # Формируем клавиатуру: суммы по 2 в ряд, затем копировать, затем 'Я задонатил!'
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            buttons[i:i + 2] for i in range(0, len(buttons), 2)
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
        "После проверки админом ты получишь 500 баллов и статус Supporter!"
    )
    await state.set_state(DonateStates.waiting_proof)

@router.message(Command("donate"))
async def donate_handler(msg: Message):
    if msg.chat.type in ("group", "supergroup"):
        # Рекламное сообщение с кнопкой перехода в личку
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="💎 Донатить в личке боту",
                    url=f"https://t.me/{BOT_USERNAME}?start=donate"
                )]
            ]
        )
        await msg.answer(
            "💎 <b>Поддержи проект Sisu Datu Bot!</b>\n\n"
            "Стань Supporter и получи плюшки:\n"
            "• Бейдж в профиле и топе\n"
            "• Приоритет в поддержке\n"
            "• В будущем — эксклюзивные фичи и розыгрыши!\n\n"
            "<i>Для приватности донать только в личке с ботом!</i>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return
    # В личке — полноценный процесс доната
    keyboard = get_donate_keyboard()
    await msg.answer(
        "🙏 Спасибо за желание поддержать проект!\n\n"
        f"<b>TON-кошелек для доната:</b> <code>{TON_WALLET}</code>\n\n"
        "Выбери сумму для поддержки через мобильный TON-кошелек (например, Tonkeeper) или скопируй адрес для ручного перевода.\n\n"
        "<i>Кнопки работают только на мобильных устройствах с установленным TON-кошельком!</i>\n\n"
        "• 0.5 TON — небольшая поддержка\n"
        "• 1 TON — стандартная поддержка\n"
        "• 2 TON — значительная поддержка\n"
        "• 5 TON — VIP поддержка\n"
        "• Другая сумма — укажи сам\n\n"
        "<b>Что дает статус поддержки?</b>\n"
        "• Благодарность от команды и бейдж в профиле\n"
        "• Приоритет в ответах и поддержке\n"
        "• Возможность влиять на развитие проекта\n"
        "• В будущем — эксклюзивные фичи и розыгрыши!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(Command("start"))
async def start_donate_handler(msg: Message):
    # Если пользователь зашел по deep link /start donate, сразу показываем донат-меню
    if msg.chat.type == "private" and msg.text.strip().startswith("/start donate"):
        keyboard = get_donate_keyboard()
        await msg.answer(
            "🙏 Спасибо за желание поддержать проект!\n\n"
            f"<b>TON-кошелек для доната:</b> <code>{TON_WALLET}</code>\n\n"
            "Выбери сумму для поддержки через мобильный TON-кошелек (например, Tonkeeper) или скопируй адрес для ручного перевода.\n\n"
            "<i>Кнопки работают только на мобильных устройствах с установленным TON-кошельком!</i>\n\n"
            "• 0.5 TON — небольшая поддержка\n"
            "• 1 TON — стандартная поддержка\n"
            "• 2 TON — значительная поддержка\n"
            "• 5 TON — VIP поддержка\n"
            "• Другая сумма — укажи сам\n\n"
            "<b>Что дает статус поддержки?</b>\n"
            "• Благодарность от команды и бейдж в профиле\n"
            "• Приоритет в ответах и поддержке\n"
            "• Возможность влиять на развитие проекта\n"
            "• В будущем — эксклюзивные фичи и розыгрыши!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@router.message(DonateStates.waiting_proof)
async def handle_donate_proof(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    # Пересылаем админу(ам) с кнопкой "Подтвердить донат"
    for admin_id in ADMIN_IDS:
        if msg.photo:
            await msg.bot.send_photo(admin_id, msg.photo[-1].file_id, caption=f"Донат от @{msg.from_user.username or msg.from_user.id}\nID: {user_id}",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Подтвердить донат", callback_data=f"approve_donate_{user_id}")]]))
        elif msg.document:
            await msg.bot.send_document(admin_id, msg.document.file_id, caption=f"Донат от @{msg.from_user.username or msg.from_user.id}\nID: {user_id}",
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Подтвердить донат", callback_data=f"approve_donate_{user_id}")]]))
        else:
            await msg.bot.send_message(admin_id, f"Донат от @{msg.from_user.username or msg.from_user.id}\nID: {user_id}\n\n{msg.text}",
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Подтвердить донат", callback_data=f"approve_donate_{user_id}")]]))
    await msg.answer("Спасибо! Сообщение отправлено админу. Ожидай подтверждения.")
    await state.clear()

@router.callback_query(lambda c: c.data and c.data.startswith("approve_donate_"))
async def approve_donate_callback(call: CallbackQuery):
    user_id = call.data.split("_")[-1]
    user = points_service.set_supporter(user_id)
    user = points_service.add_points(user_id, 500)
    # Уведомляем пользователя
    try:
        await call.bot.send_message(user_id, "🎉 Твой донат подтвержден!\n\nТы получил 500 баллов и статус Supporter. Спасибо за поддержку!")
    except Exception:
        pass
    # Публичное сообщение в группу
    try:
        username = user.get("username")
        name = username and f"@{username}" or f"ID {user_id}"
        await call.bot.send_message(
            SUPPORTER_ANNOUNCE_CHAT_ID,
            f"🎉 {name} поддержал проект и стал Supporter!\nСпасибо за вклад в развитие Sisu Datu Bot! 🐉💎"
        )
    except Exception:
        pass
    await call.answer("Донат подтвержден, статус и баллы начислены!", show_alert=True) 
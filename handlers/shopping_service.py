import logging

from aiogram import Router, types, F
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from aiogram.fsm.context import FSMContext

from config import ADMINS_IDS, USER_TYPE_GARANT, USER_TYPE_TRUSTED_GARANT, USER_TYPE_SCAMMER
from database import add_user_garant, get_user_type
from utils import (
    BuyStates,
    get_buy_skip_keyboard,
    get_buy_cancel_keyboard,
    get_buy_payment_keyboard,
)

logger = logging.getLogger(__name__)

router = Router()

GARANT_ROLE_NAMES = {
    "garant": USER_TYPE_GARANT,
    "trusted_garant": USER_TYPE_TRUSTED_GARANT,
}

# Цена в звёздах Telegram Stars (валюта XTR)
GARANT_PRICES = {
    "garant": 750,
    "trusted_garant": 1500,
}

NO_INFO_PLACEHOLDER = "Нет информации"


def get_buy_summary(buy_type: str, roblox_username: str, proofs: str, proofs_num) -> str:
    role_name = GARANT_ROLE_NAMES.get(buy_type, USER_TYPE_GARANT)
    stars = GARANT_PRICES.get(buy_type, GARANT_PRICES["garant"])

    return (
        f"💎 <b>Звание:</b> {role_name}\n"
        f"🎮 <b>Roblox ник:</b> {roblox_username}\n"
        f"🔗 <b>Пруфы:</b> {proofs}\n"
        f"🔢 <b>Кол-во пруфов:</b> {proofs_num if proofs_num is not None else NO_INFO_PLACEHOLDER}\n\n"
        f"⏳ <b>Срок:</b> 1 месяц\n"
        f"⭐ <b>Цена:</b> {stars}⭐\n\n"
        "✅ Если всё верно — оплатите покупку 👇"
    )


async def notify_admins_about_purchase(bot, message: Message, data: dict):
    """Отправляет админам сообщение о купленном гаранте со всей информацией о пользователе."""
    user = message.from_user
    buy_type = data.get("buy_type", "garant")
    role_name = GARANT_ROLE_NAMES.get(buy_type, USER_TYPE_GARANT)
    stars = GARANT_PRICES.get(buy_type, GARANT_PRICES["garant"])

    username_text = f"@{user.username}" if user.username else "нет @username"

    response_text = (
        "🛒 <b>Новая покупка гаранта!</b>\n\n"
        f"👤 <b>Пользователь:</b> {username_text}\n"
        f"ℹ <b>ID:</b> <code>{user.id}</code>\n"
        f"📛 <b>Имя:</b> {user.full_name}\n"
        f"💎 <b>Купил звание:</b> {role_name}\n"
        f"🎮 <b>Roblox ник:</b> {data.get('roblox_username')}\n"
        f"🔗 <b>Пруфы:</b> {data.get('proofs')}\n"
        f"🔢 <b>Кол-во пруфов:</b> {data.get('proofs_num') if data.get('proofs_num') is not None else NO_INFO_PLACEHOLDER}\n"
        f"⏳ <b>Срок:</b> 1 месяц\n"
        f"⭐ <b>Оплачено:</b> {stars}⭐"
    )

    for admin_id in ADMINS_IDS:
        try:
            await bot.send_message(admin_id, response_text)
        except Exception as e:
            logger.warning("Failed to notify admin %s about purchase: %s", admin_id, e)


@router.callback_query(F.data == "buy_back")
async def handle_buy_back(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.answer()


@router.callback_query(F.data == "buy:cancel")
async def handle_buy_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Покупка отменена. Возвращайтесь в меню 👇")
    await callback.answer("Отменено")


@router.callback_query(F.data == "buy_garant")
async def handle_buy_garant(callback: CallbackQuery, state: FSMContext):
    await start_buy_flow(callback, state, "garant")


@router.callback_query(F.data == "buy_trusted_garant")
async def handle_buy_trusted_garant(callback: CallbackQuery, state: FSMContext):
    await start_buy_flow(callback, state, "trusted_garant")


async def start_buy_flow(callback: CallbackQuery, state: FSMContext, buy_type: str):
    user_type, *_ = await get_user_type(callback.from_user.id)

    if user_type == USER_TYPE_SCAMMER:
        await callback.answer("Скаммеры не могут покупать гаранта ❌", show_alert=True)
        return

    role_name = GARANT_ROLE_NAMES.get(buy_type, USER_TYPE_GARANT)
    stars = GARANT_PRICES.get(buy_type, GARANT_PRICES["garant"])

    await state.update_data(buy_type=buy_type)
    await state.set_state(BuyStates.waiting_for_roblox_username)

    await callback.message.answer(
        f"💎 <b>Покупка звания:</b> {role_name} ({stars}⭐, на 1 месяц)\n\n"
        "🎮 Шаг 1/3: Введите <b>ваш никнейм в Roblox</b>:",
        reply_markup=get_buy_cancel_keyboard(),
    )
    await callback.answer()


@router.message(BuyStates.waiting_for_roblox_username)
async def handle_buy_roblox_username(message: types.Message, state: FSMContext):
    roblox_username = message.text.strip()

    if not roblox_username:
        await message.answer("❗ Никнейм не может быть пустым. Попробуйте ещё раз:")
        return

    await state.update_data(roblox_username=roblox_username)
    await state.set_state(BuyStates.waiting_for_proofs)

    await message.answer("🔗 Шаг 2/3: Отправьте <b>пруфы</b> (ссылки/описание доказательств):")


@router.message(BuyStates.waiting_for_proofs)
async def handle_buy_proofs(message: types.Message, state: FSMContext):
    proofs = message.text.strip()

    if not proofs:
        await message.answer("❗ Пруфы не могут быть пустыми. Попробуйте ещё раз:")
        return

    await state.update_data(proofs=proofs)
    await state.set_state(BuyStates.waiting_for_proofs_num)

    await message.answer("🔢 Шаг 3/3: Введите <b>количество пруфов</b>:")


@router.message(BuyStates.waiting_for_proofs_num)
async def handle_buy_proofs_num(message: types.Message, state: FSMContext):
    proofs_num = message.text.strip()

    if not proofs_num:
        await message.answer("❗ Количество пруфов не может быть пустым. Попробуйте ещё раз:")

    if not proofs_num.isdigit():
        await message.answer("❗ Количество пруфов должно быть целым числом. Попробуйте ещё раз:")
        return

    await state.update_data(proofs_num=int(proofs_num))
    await ask_payment(message, state)


async def ask_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    buy_type = data.get("buy_type", "garant")
    stars = GARANT_PRICES.get(buy_type, GARANT_PRICES["garant"])

    await state.set_state(BuyStates.waiting_for_payment)

    await message.answer(
        f"📋 <b>Проверьте информацию перед покупкой:</b>\n\n"
        f"{get_buy_summary(buy_type, data.get('roblox_username'), data.get('proofs'), data.get('proofs_num'))}",
        reply_markup=get_buy_payment_keyboard(stars),
    )


@router.callback_query(BuyStates.waiting_for_payment, F.data == "buy:pay")
async def handle_buy_pay(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    buy_type = data.get("buy_type", "garant")
    role_name = GARANT_ROLE_NAMES.get(buy_type, USER_TYPE_GARANT)
    stars = GARANT_PRICES.get(buy_type, GARANT_PRICES["garant"])

    await callback.message.answer_invoice(
        title=f"Покупка гаранта — {role_name}",
        description=(
            f"Звание {role_name} на 1 месяц. "
            f"Roblox ник: {data.get('roblox_username')}. "
            f"Пруфы: {data.get('proofs')}"
        ),
        payload=f"buy_{buy_type}_month",
        currency="XTR",
        prices=[LabeledPrice(label=role_name, amount=stars)],
    )
    await callback.answer()


@router.pre_checkout_query()
async def handle_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def handle_successful_payment(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    buy_type = data.get("buy_type", "garant")
    role_name = GARANT_ROLE_NAMES.get(buy_type, USER_TYPE_GARANT)

    # Выдаём звание гаранта на месяц
    await add_user_garant(
        message.from_user.id,
        garant_name=role_name,
        roblox_username=data.get("roblox_username"),
        proofs=data.get("proofs"),
        proofs_num=data.get("proofs_num"),
        duration_days=30,
    )

    await state.clear()

    await message.answer(
        f"✅ <b>Спасибо за покупку!</b>\n\n"
        f"💎 Вам выдано звание <b>{role_name}</b> на 1 месяц 📅\n"
        "Проверить себя можно командой /me или кнопкой «Проверить вас» в меню."
    )

    # Уведомляем админов о покупке со всей информацией
    await notify_admins_about_purchase(bot, message, data)
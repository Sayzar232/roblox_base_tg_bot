import logging

from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import ADMINS_IDS, USER_TYPE_GARANT, USER_TYPE_TRUSTED_GARANT
from database import db
from utils import (
    get_admin_keyboard,
    get_admin_role_keyboard,
    get_admin_duration_keyboard,
    get_admin_skip_keyboard,
    AdminStates,
    get_admin_cancel_keyboard
)

logger = logging.getLogger(__name__)

GARANT_ROLE_NAMES = {
    "garant": USER_TYPE_GARANT,
    "trusted_garant": USER_TYPE_TRUSTED_GARANT,
}

NO_INFO_PLACEHOLDER = "Нет информации"

router = Router()


async def send_broadcast_text(users, message_text, bot: Bot):
    sent_count = 0
    for user in users:
        try:
            await bot.send_message(user["id"], message_text, parse_mode="HTML")
            sent_count += 1
        except Exception as e:
            logger.warning("Failed to send broadcast to user %s: %s", user, e)

    return sent_count


@router.message(Command("admin"))
async def handle_command_admin(message: types.Message):
    user_id = message.from_user.id

    if user_id not in ADMINS_IDS:
        return

    response_text = (
        "⚙ <b>Админ панель</b>\n\n"
        "<b>Здесь можно:</b>\n"
        "• 📈 Проверить статистику пользователей и бота\n"
        "• 💎 Выдать кому-то звание гаранта/скаммера\n"
        "• 📩 Сделать рассылку сообщений ко всем пользователям\n\n"
        "<b>Админ панель снизу 👇</b>"
    )

    await message.answer(response_text, reply_markup=get_admin_keyboard())


@router.callback_query(F.data == "admin_stats")
async def handle_admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS_IDS:
        return

    stats = await db.get_admin_stats()

    response_text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👤 <b>Всего пользователей:</b> {stats['users']}\n"
        f"🆕 <b>Новых за сегодня:</b> {stats['users_today']}\n\n"
        f"💎 <b>Активных гарантов:</b> {stats['garants']}\n"
        f"❌ <b>Скаммеров:</b> {stats['scammers']}\n\n"
    )

    await callback.message.edit_text(response_text, reply_markup=get_admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_give_garant")
async def handle_admin_give_garant(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.set_state(AdminStates.waiting_for_user)
    await callback.message.edit_text(
        "👤 Отправьте ID или @username пользователя, которому нужно выдать звание."
    )
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def handle_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.set_state(AdminStates.waiting_for_broadcast_text)
    await callback.message.edit_text(
        "📝 <b>Теперь введите текст для рассылки.</b>\n\n<i>Используется HTML форматирование</i>",
        reply_markup=get_admin_cancel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_cancel")
async def handle_admin_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text("❌ Вы отменили рассылку", reply_markup=get_admin_keyboard())

    await callback.answer()


@router.message(F.text, AdminStates.waiting_for_broadcast_text)
async def handle_admin_text_broadcast(message: types.Message, state: FSMContext, bot: Bot):
    if message.from_user.id not in ADMINS_IDS:
        return

    users = await db.get_all_users()

    sent_count = await send_broadcast_text(users, message.text, bot)

    await message.answer(f"Было отправлено: {sent_count} сообщений")

    await state.clear()


@router.message(AdminStates.waiting_for_user)
async def handle_admin_give_user(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS_IDS:
        await state.clear()
        return

    argument = message.text.strip()

    if argument.lstrip("@").isdigit():
        user_id = int(argument.lstrip("@"))
        username = None
        full_name = None

        # Пытаемся подтянуть данные пользователя из Telegram (best-effort)
        try:
            chat = await message.bot.get_chat(user_id)
            username = chat.username
            full_name = chat.full_name
        except Exception:
            pass

        # Создаём запись в users, если пользователя там ещё нет,
        # иначе выдача звания упадёт из-за внешнего ключа
        was_created = await db.ensure_user_exists(user_id, username=username, full_name=full_name)
    else:
        user_id = await db.get_user_id_by_username(argument)

        if user_id is None:
            await message.answer(
                "❗ Пользователь с таким @username не найден в базе данных.\n"
                "Пожалуйста, введите id пользователя."
            )
            return

        was_created = False

    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminStates.waiting_for_role)

    created_note = "\n\n🆕 Пользователь добавлен в базу данных." if was_created else ""

    await message.answer(
        f"👤 <b>Пользователь:</b> <code>{user_id}</code>\n\n"
        f"💎 Выберите, какое звание выдать:{created_note}",
        reply_markup=get_admin_role_keyboard(),
    )


@router.callback_query(AdminStates.waiting_for_role, F.data == "admin:role:garant")
async def handle_admin_role_garant(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.update_data(garant_role="garant")
    await state.set_state(AdminStates.waiting_for_roblox_username)
    await callback.message.edit_text(
        "🎮 Введите <b>никнейм пользователя в Roblox</b>, которого выдаём гарантом:",
        reply_markup=get_admin_skip_keyboard(),
    )
    await callback.answer()


@router.callback_query(AdminStates.waiting_for_role, F.data == "admin:role:trusted_garant")
async def handle_admin_role_trusted_garant(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.update_data(garant_role="trusted_garant")
    await state.set_state(AdminStates.waiting_for_roblox_username)
    await callback.message.edit_text(
        "🎮 Введите <b>никнейм пользователя в Roblox</b>, которого выдаём проверенным гарантом:",
        reply_markup=get_admin_skip_keyboard(),
    )
    await callback.answer()


@router.callback_query(AdminStates.waiting_for_roblox_username, F.data == "admin:skip")
async def handle_admin_garant_skip_roblox_username(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.update_data(roblox_username=NO_INFO_PLACEHOLDER)
    await state.set_state(AdminStates.waiting_for_proofs)

    await callback.message.edit_text("🔗 Отправьте <b>пруфы</b> (ссылки/описание доказательств):")
    await callback.answer("Пропущено")


@router.message(AdminStates.waiting_for_roblox_username)
async def handle_admin_garant_roblox_username(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS_IDS:
        await state.clear()
        return

    roblox_username = message.text.strip()

    await state.update_data(roblox_username=roblox_username)
    await state.set_state(AdminStates.waiting_for_proofs)

    await message.answer("🔗 Отправьте <b>пруфы</b> (ссылка на канал/чат):")


@router.message(AdminStates.waiting_for_proofs)
async def handle_admin_garant_proofs(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS_IDS:
        await state.clear()
        return

    proofs = message.text.strip()

    await state.update_data(proofs=proofs)
    await state.set_state(AdminStates.waiting_for_proofs_num)

    await message.answer(
        "🔢 Введите <b>количество пруфов</b>:",
        reply_markup=get_admin_skip_keyboard(),
    )


@router.callback_query(AdminStates.waiting_for_proofs_num, F.data == "admin:skip")
async def handle_admin_garant_skip_proofs_num(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.update_data(proofs_num=None)
    await state.set_state(AdminStates.waiting_for_duration)

    data = await state.get_data()
    user_id = data.get("target_user_id")
    garant_role = data.get("garant_role")
    role_name = GARANT_ROLE_NAMES.get(garant_role, USER_TYPE_GARANT)

    await callback.message.edit_text(
        f"👤 <b>Пользователь:</b> <code>{user_id}</code>\n"
        f"💎 <b>Звание:</b> {role_name}\n"
        f"🎮 <b>Roblox ник:</b> {data.get('roblox_username')}\n"
        f"🔗 <b>Пруфы:</b> {data.get('proofs')}\n"
        f"🔢 <b>Кол-во пруфов:</b> {NO_INFO_PLACEHOLDER}\n\n"
        "⏳ Выберите, на какой срок выдать гаранта:",
        reply_markup=get_admin_duration_keyboard(),
    )
    await callback.answer("Пропущено")


@router.message(AdminStates.waiting_for_proofs_num)
async def handle_admin_garant_proofs_num(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS_IDS:
        await state.clear()
        return

    proofs_num = message.text.strip()

    if not proofs_num.isdigit():
        await message.answer("❗ Количество пруфов должно быть целым числом. Попробуйте ещё раз:")
        return

    await state.update_data(proofs_num=int(proofs_num))
    await state.set_state(AdminStates.waiting_for_duration)

    data = await state.get_data()
    user_id = data.get("target_user_id")
    garant_role = data.get("garant_role")
    role_name = GARANT_ROLE_NAMES.get(garant_role, USER_TYPE_GARANT)

    await message.answer(
        f"👤 <b>Пользователь:</b> <code>{user_id}</code>\n"
        f"💎 <b>Звание:</b> {role_name}\n"
        f"🎮 <b>Roblox ник:</b> {data.get('roblox_username')}\n"
        f"🔗 <b>Пруфы:</b> {data.get('proofs')}\n"
        f"🔢 <b>Кол-во пруфов:</b> {proofs_num}\n\n"
        "⏳ Выберите, на какой срок выдать гаранта:",
        reply_markup=get_admin_duration_keyboard(),
    )


@router.callback_query(AdminStates.waiting_for_duration, F.data.in_({"admin:duration:forever", "admin:duration:month"}))
async def handle_admin_garant_duration(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    duration = callback.data.split(":")[-1]
    duration_days = None if duration == "forever" else 30

    data = await state.get_data()
    user_id = data.get("target_user_id")
    garant_role = data.get("garant_role", "garant")
    garant_name = GARANT_ROLE_NAMES.get(garant_role, USER_TYPE_GARANT)

    await db.add_user_garant(
        user_id,
        garant_name=garant_name,
        roblox_username=data.get("roblox_username"),
        proofs=data.get("proofs"),
        proofs_num=data.get("proofs_num"),
        duration_days=duration_days,
    )
    await state.clear()

    duration_text = "♾ <b>навсегда</b>" if duration_days is None else "📅 <b>на месяц</b>"
    await callback.message.edit_text(
        f"✅ Пользователь <code>{user_id}</code> получил звание <b>{garant_name}</b> 💎\n"
        f"⏳ Срок: {duration_text}"
    )
    await callback.answer("Звание выдано")


@router.callback_query(AdminStates.waiting_for_role, F.data == "admin:role:scammer")
async def handle_admin_role_scammer(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.set_state(AdminStates.waiting_for_reason)
    await callback.message.edit_text("❌ Опишите причину, по которой пользователь попадает в скаммеры:")
    await callback.answer()


@router.message(AdminStates.waiting_for_reason)
async def handle_admin_scammer_reason(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS_IDS:
        await state.clear()
        return

    reason = message.text.strip()
    data = await state.get_data()
    user_id = data.get("target_user_id")

    await db.add_user_scammer(user_id, reason)
    await state.clear()

    await message.answer(f"✅ Пользователь <code>{user_id}</code> получил звание <b>Скаммер</b> ❌")


@router.callback_query(F.data == "admin:role:cancel")
async def handle_admin_role_cancel(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.clear()
    await callback.message.edit_text("⚙ <b>Админ панель</b>", reply_markup=get_admin_keyboard())
    await callback.answer("Отменено")
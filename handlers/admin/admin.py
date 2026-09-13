from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import ADMINS_IDS, USER_TYPE_GARANT, USER_TYPE_TRUSTED_GARANT
from database import get_admin_stats, get_user_id_by_username, add_user_garant, add_user_scammer
from utils import get_admin_keyboard, get_admin_role_keyboard, AdminStates

router = Router()


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

    stats = await get_admin_stats()

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


@router.message(AdminStates.waiting_for_user)
async def handle_admin_give_user(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS_IDS:
        await state.clear()
        return

    argument = message.text.strip()

    if argument.lstrip("@").isdigit():
        user_id = int(argument.lstrip("@"))
    else:
        user_id = await get_user_id_by_username(argument)

        if user_id is None:
            await message.answer(
                "❗ Пользователь с таким @username не найден в базе данных.\n"
                "Пожалуйста, введите id пользователя."
            )
            return

    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminStates.waiting_for_role)

    await message.answer(
        f"👤 <b>Пользователь:</b> <code>{user_id}</code>\n\n"
        "💎 Выберите, какое звание выдать:",
        reply_markup=get_admin_role_keyboard(),
    )


@router.callback_query(AdminStates.waiting_for_role, F.data == "admin:role:garant")
async def handle_admin_role_garant(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    data = await state.get_data()
    user_id = data.get("target_user_id")

    await add_user_garant(user_id, USER_TYPE_GARANT)
    await state.clear()

    await callback.message.edit_text(f"✅ Пользователь <code>{user_id}</code> получил звание <b>Гаранта</b> 💎")
    await callback.answer("Звание выдано")


@router.callback_query(AdminStates.waiting_for_role, F.data == "admin:role:trusted_garant")
async def handle_admin_role_trusted_garant(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    data = await state.get_data()
    user_id = data.get("target_user_id")

    await add_user_garant(user_id, USER_TYPE_TRUSTED_GARANT)
    await state.clear()

    await callback.message.edit_text(f"✅ Пользователь <code>{user_id}</code> получил звание <b>Проверенного Гаранта</b> 💎")
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

    await add_user_scammer(user_id, reason)
    await state.clear()

    await message.answer(f"✅ Пользователь <code>{user_id}</code> получил звание <b>Скаммер</b> ❌")


@router.callback_query(AdminStates.waiting_for_role, F.data == "admin:role:cancel")
async def handle_admin_role_cancel(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS_IDS:
        return

    await state.clear()
    await callback.message.edit_text("⚙ <b>Админ панель</b>", reply_markup=get_admin_keyboard())
    await callback.answer("Отменено")
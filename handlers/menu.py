from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from utils import MenuStates, get_command_id_keyboard
from database import get_user_type

router = Router()


@router.message(MenuStates.waiting_for_id)
async def handle_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста введите правильный id")
        return

    user_id = int(message.text)

    user_type, username, *_= await get_user_type(int(user_id))

    response_text = (
        f"<b>{user_type}</b>\n\n"
        f"<b>ID:</b> <code>{user_id}</code>\n"
        f"<b>Пользователь:</b> @{username}\n"
    )

    await message.answer(response_text)
    await state.clear()


@router.callback_query(F.data == "menu_check_user")
async def handle_menu_check_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Теперь отправьте id пользователя")

    await state.set_state(MenuStates.waiting_for_id)
    await callback.answer()


@router.callback_query(F.data == "menu_check_me")
async def handle_menu_check_me(callback: CallbackQuery):
    user_id = callback.message.from_user.id
    username = callback.message.from_user.username
    user_type, *_ = await get_user_type(user_id)

    response_text = (
        f"<b>{user_type}</b>\n\n"
        f"ID: {user_id}\n"
        f"Пользователь: @{username}"
    )

    await callback.message.answer(response_text)
    await callback.answer()


@router.callback_query(F.data == "menu_get_id")
async def handle_menu_check_me(callback: CallbackQuery):
    await callback.message.answer(f"<b>Выберите объект для получения ID 👇:</b>", reply_markup=get_command_id_keyboard())

    await callback.answer()
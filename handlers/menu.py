from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from utils import MenuStates, get_command_id_keyboard
from database import get_user_type
from .user_commands import send_user_type_message

router = Router()


@router.message(MenuStates.waiting_for_id)
async def handle_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста введите правильный id")
        return

    user_id = int(message.text)

    user_type, username, *_= await get_user_type(int(user_id))

    await send_user_type_message(message, user_id, username, user_type)

    await state.clear()


@router.callback_query(F.data == "menu_check_user")
async def handle_menu_check_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Теперь отправьте id пользователя")

    await state.set_state(MenuStates.waiting_for_id)
    await callback.answer()


@router.callback_query(F.data == "menu_check_me")
async def handle_menu_check_me(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    user_type, *_ = await get_user_type(user_id)

    await send_user_type_message(callback.message, user_id, username, user_type)

    await callback.answer()


@router.callback_query(F.data == "menu_get_id")
async def handle_menu_get_id(callback: CallbackQuery):
    await callback.message.answer(f"<b>Выберите объект для получения ID 👇:</b>", reply_markup=get_command_id_keyboard())

    await callback.answer()
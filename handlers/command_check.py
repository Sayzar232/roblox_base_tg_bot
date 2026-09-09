from aiogram import Router, types
from aiogram.filters import Command

from database.database import get_user_type

router = Router()


@router.message(Command("check"))
async def handle_check_command(message: types.Message):
    user_id = message.text.replace("/check", "").strip()

    if not user_id or not user_id.isdigit():
        await message.answer("Пожалуйста, введите id пользователя после команды.")
        return

    user_type, username, full_name = await get_user_type(int(user_id))

    response_text = (
        f"<b>{user_type}</b>\n\n"
        f"ID: {user_id}\n"
        f"Пользователь: @{username}\n"
    )
    
    await message.answer(response_text)
from aiogram import Router, types
from aiogram.filters import Command

from database.database import get_user_type

router = Router()


@router.message(Command("me"))
async def handle_me_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    user_type, *_ = await get_user_type(user_id)

    response_text = (
        f"<b>{user_type}</b>\n\n"
        f"ID: {user_id}\n"
        f"Пользователь: @{username}"
    )

    await message.answer(response_text)
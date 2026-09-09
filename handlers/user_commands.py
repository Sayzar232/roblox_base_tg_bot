from aiogram import Router, types
from aiogram.filters import Command, CommandStart

from database.database import get_user_type, add_user
from utils.reply_keyboards import get_command_id_keyboard, get_reply_keyboard

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


@router.message(Command("id"))
async def handle_check_command(message: types.Message):
    await message.answer(f"Выберите объект для получения ID:", reply_markup=get_command_id_keyboard())


@router.message(CommandStart())
async def start_message(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer("Hello, this is a simple bot!", reply_markup=get_reply_keyboard())
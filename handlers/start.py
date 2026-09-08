from aiogram import Router, types
from aiogram.filters import CommandStart

from utils.reply_keyboards import get_reply_keyboard
from database.database import add_user

router = Router()


@router.message(CommandStart())
async def start_message(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer("Hello, this is a simple bot!", reply_markup=get_reply_keyboard())
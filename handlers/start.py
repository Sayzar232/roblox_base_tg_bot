from aiogram import Router, types
from aiogram.filters import CommandStart

from utils.reply_keyboards import get_reply_keyboard

router = Router()


@router.message(CommandStart())
async def start_message(message: types.Message):
    await message.answer("Hello, this is a simple bot!", reply_markup=get_reply_keyboard())
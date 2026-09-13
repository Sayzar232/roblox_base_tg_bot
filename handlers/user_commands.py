from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile

from database import get_user_type, get_user_id_by_username, add_user
from utils import get_command_id_keyboard, get_menu_keyboard
from config import (
    GARANT_PHOTO_PATH,
    TRUSTED_GARANT_PHOTO_PATH,
    SCAM_PHOTO_PATH,
    USER_PHOTO_PATH,
    USER_TYPE_USER,
    USER_TYPE_GARANT,
    USER_TYPE_SCAMMER,
    USER_TYPE_TRUSTED_GARANT
)

router = Router()

start_text = """
<b>🖐 Добро пожаловать в базу гарантов по Roblox!</b>

Это бот, в котором игроки Roblox могут узнать является ли <b>гарант мошенником</b>, а также пожаловаться на него, чтобы другие не попались на него

<b>🤖 Что умеет этот бот:</b>

• ❌ проверять репутацию пользователей в сфере, что бы уменьшить шанс скама
• 🆘 Пожаловаться на скам
• 🔍 Найти себе верного гаранта

<b>Нажимай на кнопки в меню и начинай 👇</b>
"""


def get_path_by_type(user_type: str):
    if user_type == USER_TYPE_USER:
        return USER_PHOTO_PATH
    elif user_type == USER_TYPE_GARANT:
        return GARANT_PHOTO_PATH
    elif user_type == USER_TYPE_SCAMMER:
        return SCAM_PHOTO_PATH
    elif user_type == USER_TYPE_TRUSTED_GARANT:
        return TRUSTED_GARANT_PHOTO_PATH

    return USER_PHOTO_PATH


async def send_user_type_message(message: types.Message, user_id, username, user_type):
    response_text = (
        f"🔷 <b>{user_type}</b> 🔷\n\n"
        f"ℹ <b>ID:</b> <code>{user_id}</code>\n"
        f"👤 <b>Пользователь:</b> @{username}"
    )

    if username is None and user_type == USER_TYPE_USER:
        response_text = (
            f"🔷 <b>{user_type}</b> 🔷\n\n"
            f"ℹ <b>ID:</b> <code>{user_id}</code>\n"
            f"❗ Внимание, информации о данном пользователе нет в базе данных, будьте осторожны, если он предлагает вам услуги"
        )

    image_path = get_path_by_type(user_type)

    await message.answer_photo(FSInputFile(image_path), caption=response_text)


@router.message(CommandStart())
async def start_message(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(start_text, reply_markup=get_menu_keyboard())


@router.message(Command("me"))
async def handle_me_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    user_type, *_ = await get_user_type(user_id)

    await send_user_type_message(message, user_id, username, user_type)


@router.message(Command("check"))
async def handle_check_command(message: types.Message):
    argument = message.text.replace("/check", "", 1).strip()

    if not argument:
        await message.answer(
            "Пожалуйста, укажите id или @username пользователя после команды.\n"
            "Примеры: <code>/check 123456789</code> или <code>/check @username</code>"
        )
        return

    # Если аргумент — @username или не число, ищем пользователя по username
    if argument.lstrip("@").isdigit():
        user_id = int(argument.lstrip("@"))
    else:
        user_id = await get_user_id_by_username(argument)

        if user_id is None:
            await message.answer("❗ Пользователь с таким @username не найден в базе данных.")
            return

    user_type, username, *_ = await get_user_type(user_id)

    await send_user_type_message(message, user_id, username, user_type)


@router.message(Command("id"))
async def handle_get_id(message: types.Message):
    await message.answer(f"<b>Выберите объект для получения ID 👇:</b>", reply_markup=get_command_id_keyboard())
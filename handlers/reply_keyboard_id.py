from aiogram import Router, types, F
from utils.reply_keyboards import get_menu_keyboard

router = Router()


@router.message(F.text == "Выбрать канал")
@router.message(F.text == "Выбрать группу")
@router.message(F.text == "Выбрать пользователя")
async def handle_select_request(message: types.Message):
    pass


@router.message(F.users_shared)
async def handle_users_shared(message: types.Message):
    users_shared = message.users_shared

    response_text = "<b>Пользователь:</b>\n"
    for shared_user in users_shared.users:
        user_id = shared_user.user_id
        
        response_text += f"<b>ID:</b> <code>{user_id}</code>"

    await message.answer(response_text)


@router.message(F.chat_shared)
async def handle_chat_shared(message: types.Message):
    chat_shared = message.chat_shared

    chat = None
    try:
        chat = await message.bot.get_chat(chat_shared.chat_id)
    except Exception:
        pass

    if chat is not None:
        title = chat.title or chat.full_name
        username = f"\nПользователь: @{chat.username}" if chat.username else ""
        await message.answer(
            f"<b>{title}</b>\n\n"
            f"ID: <code>{chat_shared.chat_id}</code>"
            f"{username}"
        )
    else:
        await message.answer(f"ID: <code>{chat_shared.chat_id}</code>")


@router.message(F.text == "Вернуться в меню")
async def handle_back_to_menu(message: types.Message):
    await message.answer("Возвращаемся в меню 👇", reply_markup=get_menu_keyboard())
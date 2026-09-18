from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config import POST_COLORS
from database import db
from utils import (
    get_menu_keyboard,
    get_post_bot_keyboard,
    get_post_creation_keyboard,
    get_post_skip_keyboard,
    get_post_favorite_keyboard,
    get_post_keyboard,
    PostStates
)

router = Router()

CALLBACK_POST_CANCEL = "post:cancel"
CALLBACK_POST_SAVE = "post:save"

BUTTONS_HINT = (
    "Каждая кнопка — с новой строки в формате:\n"
    "<b>Текст + url + цвет</b>\n\n"
    "Цвет: <code>danger</code>, <code>success</code> или <code>primary</code>\n"
    "Пример:\n"
    "<code>Поддержка + https://example.com + primary</code>"
)


def parse_post_buttons(raw_text: str) -> list:
    buttons = []

    for line in raw_text.strip().splitlines():
        parts = [part.strip() for part in line.split("+")]

        if len(parts) != 3:
            raise ValueError("Неверный формат кнопки")

        button_text, url, color = parts
        color = color.lower()

        if not button_text or not url.startswith(("http://", "https://")):
            raise ValueError("Неверный формат кнопки")

        if color not in POST_COLORS:
            raise ValueError("Неверный цвет кнопки")

        buttons.append({"text": button_text, "url": url, "color": color})

    return buttons


async def send_post_preview(message: types.Message, data: dict):
    post_text = data["text"]
    photo_file_id = data.get("photo_file_id")
    buttons = data.get("buttons") or []

    kb = get_post_keyboard(buttons)

    if photo_file_id is not None:
        await message.answer_photo(photo=photo_file_id, caption=post_text, reply_markup=kb)
    else:
        await message.answer(post_text, reply_markup=kb)


@router.message(F.text == "Назад")
async def handle_back(message: types.Message):
    await message.answer("Возвращаемся в меню 👇", reply_markup=get_menu_keyboard())


@router.message(F.text == "Избранные")
async def handle_favorite_posts(message: types.Message):
    favorite_posts = await db.get_favorite_posts(message.from_user.id)

    if not favorite_posts:
        await message.answer("У вас пока нет избранных постов.", reply_markup=get_post_bot_keyboard())
        return

    response_text = "<b>Ваши избранные посты:</b>\n\n"
    for post in favorite_posts:
        response_text += f"ID: <code>{post['id']}</code>\n\n"

    await message.answer(response_text, reply_markup=get_post_bot_keyboard())


@router.message(F.text == "Создать пост")
async def handle_create_post(message: types.Message, state: FSMContext):
    await state.set_state(PostStates.waiting_for_text)
    await message.answer(
        "✍️ Напишите текст для поста или нажмите 'Отменить создание'.",
        reply_markup=get_post_creation_keyboard(),
    )


@router.message(StateFilter(PostStates), F.text == "Отменить создание")
async def handle_cancel_creation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Создание поста отменено.", reply_markup=get_post_bot_keyboard())


@router.message(PostStates.waiting_for_text)
async def handle_post_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(PostStates.waiting_for_photo)

    await message.answer(
        "📷 Теперь отправьте фото для поста (опционально) или нажмите 'Пропустить'.",
        reply_markup=get_post_skip_keyboard(),
    )


@router.message(PostStates.waiting_for_photo, F.photo)
async def handle_post_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await state.set_state(PostStates.waiting_for_buttons)

    await message.answer(
        f"🔘 Последний шаг — отправьте кнопки для поста (опционально).\n\n{BUTTONS_HINT}\n\n"
        "Или нажмите 'Пропустить'.",
        reply_markup=get_post_skip_keyboard(),
    )


@router.message(PostStates.waiting_for_photo, F.text == "Пропустить")
async def handle_skip_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo_file_id=None)
    await state.set_state(PostStates.waiting_for_buttons)

    await message.answer(
        f"🔘 Теперь отправьте кнопки для поста (опционально).\n\n{BUTTONS_HINT}\n\n"
        "Или нажмите 'Пропустить'.",
        reply_markup=get_post_skip_keyboard(),
    )


@router.message(PostStates.waiting_for_photo)
async def handle_wrong_post_photo(message: types.Message):
    await message.answer(
        "Пожалуйста, отправьте фото или нажмите 'Пропустить'.",
        reply_markup=get_post_skip_keyboard(),
    )


@router.message(PostStates.waiting_for_buttons, F.text == "Пропустить")
async def handle_skip_buttons(message: types.Message, state: FSMContext):
    await state.update_data(buttons=None)
    await send_post_preview(message, await state.get_data())


@router.message(PostStates.waiting_for_buttons)
async def handle_post_buttons(message: types.Message, state: FSMContext):
    try:
        buttons = parse_post_buttons(message.text)
    except ValueError:
        await message.answer(
            f"❌ Неверный формат кнопок.\n\n{BUTTONS_HINT}\n\n"
            "Или нажмите 'Пропустить'.",
            reply_markup=get_post_skip_keyboard(),
        )
        return

    await state.update_data(buttons=buttons)
    await send_post_preview(message, await state.get_data())


@router.callback_query(F.data == CALLBACK_POST_SAVE)
async def handle_save_post(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not data.get("text"):
        await callback.answer("Пост уже сохранён", show_alert=True)
        return

    post_id = await db.create_post(
        callback.from_user.id,
        data["text"],
        data.get("photo_file_id"),
        data.get("buttons"),
    )

    await state.update_data(last_post_id=post_id)
    await state.set_state(None)

    await callback.message.answer(
        f"✅ Пост успешно сохранён!\n\n"
        f"ID поста: <code>{post_id}</code>\n"
        f"Используйте этот ID, чтобы публиковать пост в других группах.",
        reply_markup=get_post_favorite_keyboard(),
    )
    await callback.answer("Пост сохранён")


@router.callback_query(F.data == CALLBACK_POST_CANCEL)
async def handle_cancel_post(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer("Создание поста отменено.", reply_markup=get_post_bot_keyboard())
    await callback.answer()


@router.message(F.text == "Сохранить в избранные")
async def handle_save_to_favorites(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("last_post_id")

    if post_id is None:
        await message.answer("Нет сохранённого поста для добавления в избранные.")
        return

    await db.set_post_favorite(post_id)
    await state.update_data(last_post_id=None)

    await message.answer("✅ Пост добавлен в избранные!", reply_markup=get_post_bot_keyboard())
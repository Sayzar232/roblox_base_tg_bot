from aiogram.types import InlineKeyboardButton, KeyboardButtonRequestUsers, KeyboardButtonRequestChat
from aiogram.utils.keyboard import InlineKeyboardBuilder

CALLBACK_POST_CANCEL = "post:cancel"
CALLBACK_POST_SAVE = "post:save"


def get_post_keyboard(buttons: dict | None):
    builder = InlineKeyboardBuilder()
    
    for button in buttons:
        builder.add(InlineKeyboardButton(text=button["text"], url=button["url"]))
    builder.adjust(1)
    
    builder.row(
        InlineKeyboardButton(text="❌ Отменить создание", callback_data=CALLBACK_POST_CANCEL),
        InlineKeyboardButton(text="💾 Сохранить", callback_data=CALLBACK_POST_SAVE),
    )

    return builder.as_markup()


def get_service_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="🔷 Ранг", callback_data="services_rang"))
    builder.add(InlineKeyboardButton(text="💎 Гарант", callback_data="services_garant"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="services_back"))

    return builder.as_markup()


def get_menu_keyboard():
    builder = InlineKeyboardBuilder()

    # Add buttons to the keyboard
    builder.add(InlineKeyboardButton(text="Проверить пользователя", callback_data="menu_check_user"))
    builder.add(InlineKeyboardButton(text="Проверить вас", callback_data="menu_check_me"))
    builder.add(InlineKeyboardButton(text="Получить id", callback_data="menu_get_id"))
    builder.add(InlineKeyboardButton(text="Получить гаранта", callback_data="menu_buy_garant", style="primary"))
    builder.add(InlineKeyboardButton(text="Пожаловаться на скам", callback_data="menu_support_scam", style="danger"))

    # Build the keyboard
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
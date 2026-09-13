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
    return builder.as_markup()


def get_admin_role_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="✅ Выдать гаранта", callback_data="admin:role:garant"))
    builder.add(InlineKeyboardButton(text="💎 Выдать проверенного гаранта", callback_data="admin:role:trusted_garant"))
    builder.add(InlineKeyboardButton(text="❌ Выдать скаммера", callback_data="admin:role:scammer"))
    builder.add(InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:role:cancel"))

    builder.adjust(1)
    return builder.as_markup()


def get_admin_duration_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="♾ Навсегда", callback_data="admin:duration:forever"))
    builder.add(InlineKeyboardButton(text="📅 На месяц", callback_data="admin:duration:month"))
    builder.add(InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:role:cancel"))

    builder.adjust(1)
    return builder.as_markup()


def get_admin_skip_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="⏭ Пропустить", callback_data="admin:skip"))
    builder.add(InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:role:cancel"))

    builder.adjust(2)
    return builder.as_markup()


def get_admin_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Статистика бота", callback_data="admin_stats"))
    builder.add(InlineKeyboardButton(text="Выдать гаранта/скаммера", callback_data="admin_give_garant"))
    builder.add(InlineKeyboardButton(text="Сделать рассылку", callback_data="admin_broadcast"))

    builder.adjust(1)
    return builder.as_markup()
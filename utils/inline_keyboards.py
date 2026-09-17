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


# Menu keyboard
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


# Admin keyboards
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


def get_admin_cancel_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Отмена", callback_data="admin_cancel"))

    return builder.as_markup()


# Buy keyboards
def get_buy_garant_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="Гарант - 750⭐", callback_data="buy_garant"))
    builder.add(InlineKeyboardButton(text="Проверенный гарант - 1500⭐", callback_data="buy_trusted_garant"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="buy_back"))

    builder.adjust(1)
    return builder.as_markup()


def get_buy_skip_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="⏭ Пропустить", callback_data="buy:skip"))
    builder.add(InlineKeyboardButton(text="🔙 Отмена", callback_data="buy:cancel"))

    builder.adjust(2)
    return builder.as_markup()


def get_buy_cancel_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="🔙 Отмена", callback_data="buy:cancel"))

    return builder.as_markup()


def get_report_skip_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="⏭ Пропустить", callback_data="report:skip"))
    builder.add(InlineKeyboardButton(text="🔙 Отмена", callback_data="report:cancel"))

    builder.adjust(2)
    return builder.as_markup()


def get_admin_report_keyboard(target_id: int):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="🚫 Занести в базу скама", callback_data=f"report:scam:{target_id}"))

    builder.adjust(1)
    return builder.as_markup()


def get_buy_garant_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Гарант - 750⭐", callback_data="buy_garant"))
    builder.add(InlineKeyboardButton(text="Проверенный гарант - 1500⭐", callback_data="buy_trusted_garant"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="buy_back"))

    builder.adjust(1)
    return builder.as_markup()


def get_buy_payment_keyboard(stars: int):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=f"💳 Оплатить {stars}⭐", callback_data="buy:pay"))
    builder.add(InlineKeyboardButton(text="🔙 Отмена", callback_data="buy:cancel"))

    builder.adjust(1)
    return builder.as_markup()
from aiogram.types import InlineKeyboardButton
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
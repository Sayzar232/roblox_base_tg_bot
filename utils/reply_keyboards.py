from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    # Add buttons to the keyboard
    builder.add(KeyboardButton(text="Пост Бот"))
    builder.add(KeyboardButton(text="Фонд"))
    builder.add(KeyboardButton(text="Раздача"))
    builder.add(KeyboardButton(text="Карточка Базы"))
    builder.add(KeyboardButton(text="Услуги"))
    builder.add(KeyboardButton(text="Задать вопрос"))

    # Build the keyboard
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_command_id_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Выбрать канал"))
    builder.add(KeyboardButton(text="Выбрать группу"))
    builder.add(KeyboardButton(text="Выбрать пользователя"))
    builder.add(KeyboardButton(text="Вернуться в меню"))

    # Build the keyboard
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
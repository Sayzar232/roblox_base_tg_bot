from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUsers, KeyboardButtonRequestChat
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    # Add buttons to the keyboard
    builder.add(KeyboardButton(text="Пост Бот"))
    builder.add(KeyboardButton(text="Фонд"))
    builder.add(KeyboardButton(text="Карточка Базы"))
    builder.add(KeyboardButton(text="Услуги"))
    builder.add(KeyboardButton(text="Задать вопрос"))

    # Build the keyboard
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_command_id_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(
        KeyboardButton(
            text="Выбрать пользователя",
            request_users=KeyboardButtonRequestUsers(
                request_id=1,
                user_is_bot=False,
                max_quantity=1,
            ),
        )
    )
    builder.add(
        KeyboardButton(
            text="Выбрать канал",
            request_chat=KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=True,
            ),
        )
    )
    builder.add(
        KeyboardButton(
            text="Выбрать группу",
            request_chat=KeyboardButtonRequestChat(
                request_id=3,
                chat_is_channel=False,
            ),
        )
    )
    builder.add(KeyboardButton(text="Вернуться в меню"))

    # Build the keyboard
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_post_bot_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Избранные"))
    builder.add(KeyboardButton(text="Создать пост"))
    builder.add(KeyboardButton(text="Назад"))

    builder.adjust(2)
    return builder.as_markup()


def get_post_creation_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Отменить создание"))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_post_skip_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Пропустить"))
    builder.add(KeyboardButton(text="Отменить создание"))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_post_favorite_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Сохранить в избранные"))
    builder.add(KeyboardButton(text="Назад"))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
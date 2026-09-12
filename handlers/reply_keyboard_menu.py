from aiogram import Router, types, F

from utils import get_post_bot_keyboard, get_service_keyboard

router = Router()


@router.message(F.text == "Пост Бот")
async def handle_post_bot(message: types.Message):
    await message.answer("Добро пожаловать в меню Пост Бота", reply_markup=get_post_bot_keyboard())


@router.message(F.text == "Фонд")
async def handle_fund(message: types.Message):
    pass


@router.message(F.text == "Карточка Базы")
async def handle_base_card(message: types.Message):
    pass


@router.message(F.text == "Услуги")
async def handle_services(message: types.Message):
    await message.answer("<b>🛍 Выберите категорию услуг:</b>", reply_markup=get_service_keyboard())


@router.message(F.text == "Задать вопрос")
async def handle_ask_question(message: types.Message):
    pass
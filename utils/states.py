from aiogram.fsm.state import State, StatesGroup

class PostStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_buttons = State()
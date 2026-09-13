from aiogram.fsm.state import State, StatesGroup

class PostStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_buttons = State()

class MenuStates(StatesGroup):
    waiting_for_id = State()

class AdminStates(StatesGroup):
    waiting_for_user = State()
    waiting_for_role = State()
    waiting_for_reason = State()
    waiting_for_roblox_username = State()
    waiting_for_proofs = State()
    waiting_for_proofs_num = State()
    waiting_for_duration = State()
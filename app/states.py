from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    waiting_email = State()
    waiting_code = State()


class AbsenceStates(StatesGroup):
    waiting_date_choice = State()
    waiting_custom_date = State()
    waiting_reason = State()
    waiting_photo = State()

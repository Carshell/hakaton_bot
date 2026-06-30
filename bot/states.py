from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    welcome = State()
    details = State()
    name = State()
    email = State()
    telegram_username = State()
    social = State()
    works = State()
    role = State()
    role_other = State()
    workplace = State()
    workplace_other = State()
    llm_exp = State()
    tools = State()
    project = State()
    source = State()
    source_other = State()
    consent = State()
    confirmation = State()


class MenuStates(StatesGroup):
    feedback = State()


class AdminStates(StatesGroup):
    broadcast_text = State()
    broadcast_confirm = State()

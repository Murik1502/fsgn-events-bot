from aiogram.fsm.state import StatesGroup, State


class StatesForm(StatesGroup):
    pass


class CreateEvent(StatesGroup):
    step_image = State()
    step2_description = State()


class Registration(StatesGroup):
    step_start_reg = State()
    step_name = State()
    step2_surname = State()


class StartStates(StatesGroup):
    step_reg = State()

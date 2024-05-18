from aiogram.fsm.state import StatesGroup, State


class StatesForm(StatesGroup):
    pass


class CreateEvent(StatesGroup):
    step_image = State()
    step_name = State()
    step2_description = State()
    step_datetime = State()
    step_type = State()


class Registration(StatesGroup):
    step_start_reg = State()
    first_name = State()
    second_name = State()
    middle_name = State()
    group = State()


class StartStates(StatesGroup):
    step_reg = State()

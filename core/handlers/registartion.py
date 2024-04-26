from aiogram.filters import Command, StateFilter, state
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from magic_filter import F
from ..utils.statesform import *
from ..handlers import basic


class DB:
    name = ''
    surname = ''
    tg_teg = ''


reg_router = Router()


# Хэндлер на команду /reg
@reg_router.message(StateFilter(Registration.step_start_reg))
async def reg(message, state:FSMContext):
    DB.tg_teg = message.from_user.username
    await state.set_state(Registration.step_name)
    await message.answer(text='Введите имя:')


# Хэндлер на имя пользователя
@reg_router.message(StateFilter(Registration.step_name))
async def register_handler(message, state:FSMContext):
    DB.name = message.text
    await state.set_state(Registration.step2_surname)
    await message.answer(text='Введите фамилию:')



# Хэндлер на имя пользователя
@reg_router.message(StateFilter(Registration.step2_surname))
async def register_handler(message, state:FSMContext):
    DB.surname = message.text
    await state.clear()
    await message.answer("Имя:" + DB.name + "\nФамилия" + DB.surname + "\nТГ id" + DB.tg_teg)
    await basic.start_handler(message=message,state=state)

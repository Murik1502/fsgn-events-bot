from aiogram.filters import Command, StateFilter, state
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from magic_filter import F


class Admin(StatesGroup):
    step_nik = State()




give_admin_router = Router()


# Хэндлер на команду /admin
@give_admin_router.message(Command('admin'))
async def admin(message, state:FSMContext):
    await message.answer("Введите никнейм пользователя которому необходимо назначить админом:")
    await state.set_state(Admin.step_nik)


# Хэндлер на никнейм пользователя которому необходимо выдать админку
@give_admin_router.message(StateFilter(Admin.step_nik))
async def register_handler(message, state:FSMContext):
    await state.clear()
    await message.answer(text=message.text)
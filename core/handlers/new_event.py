from aiogram.filters import Command, StateFilter, state
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from magic_filter import F
import uuid


class CreateEvent(StatesGroup):
    step_image = State()
    step2_description = State()


class DB:
    image = ''
    description = ''
    type = ''
    id = ''


admin_router = Router()


# Хэндлер на команду /new_event
@admin_router.message(Command('new_event'))
async def new_event(message, state: FSMContext):
    # тут должна быть проверка на наличие у пользователя админки
    await state.set_state(CreateEvent.step_image)
    DB.id = uuid.uuid1()
    await message.answer(text='Отправте картинку для мероприятия')


# Хэндлер на команду картинку для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_image))
async def register_handler(message, state: FSMContext):
    DB.image = message.photo[-1].file_id
    await state.set_state(CreateEvent.step2_description)
    await message.answer(text='отправте описание к мероприятию')


# Хэндлер на описание для мероприятия
@admin_router.message(StateFilter(CreateEvent.step2_description))
async def register_handler(message, state: FSMContext):
    DB.description = message.text
    await state.clear()
    await message.answer_photo(photo=DB.image, caption=DB.description)
    await message.answer(DB.image)

from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext

from ..utils.statesform import *
from ..keyboards.inline import *
from ..handlers.registartion import *
from ..utils.statesform import *

router = Router()


# Хэндлер на команду /start
@router.message(Command("start"))
async def start_handler(message, state: FSMContext):
    if message.from_user.username != DB.tg_teg:  # тут должна быть проверка зарегистрирован ли пользователь
        await reg(message=message,state=state)
    else:
        await message.answer('Вы успешно зарегистрировались',reply_markup=join_event)


'''    # проверяем зарегестрирован ли полозователь
    user = 'тут данные о пользователе'
    if len(user) != 0:
        event = 'тут данные о мероприятии'
        await message.answer(event)

    if message.text == '/start 111':
        await message.answer("2")
    await message.answer('Hello')'''

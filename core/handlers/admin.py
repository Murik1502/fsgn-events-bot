from aiogram.filters import Command, StateFilter, state
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from magic_filter import F
from ..keyboards.reply import admin_keyword

import bot
from core.database import user, role, exceptions


class Admin(StatesGroup):
    step_nik = State()


give_admin_router = Router()


# Хэндлер на команду /admin
@give_admin_router.message(Command('admin'))
async def admin(message, state: FSMContext):
    user_info = user.User.fetch_by_tg_id(message.from_user.id)
    if user_info.role != role.Role.ADMIN:
        return
    await message.answer("Введите имя и фамилию пользователя, которого необходимо назначить админом:")
    await state.set_state(Admin.step_nik)


# Хэндлер на никнейм пользователя которому необходимо выдать админку
@give_admin_router.message(StateFilter(Admin.step_nik))
async def register_handler(message, state: FSMContext):
    name, surname = message.text.split()
    try:
        user_info = user.User.get_user_by_credentials(name.capitalize(), surname.capitalize())
        if user_info.role == role.Role.ADMIN:
            await message.answer("Пользователь уже является администратором!")
        else:
            user_info.role = role.Role.ADMIN
            await message.answer("Вы успешно выдали доступ пользователю!")
            await bot.bot.send_message(chat_id=user_info.telegram_id,
                                       text=f"@{message.from_user.username} выдал Вам права Администратора! Теперь с помощью кнопки /new_event вы можете создавать мероприятия",
                                       reply_markup=admin_keyword)
    except exceptions.UserNotFound:
        await message.answer("Такого пользователя не существует! Проверьте данные.")
    await state.clear()

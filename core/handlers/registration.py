from aiogram.filters import Command, StateFilter, state
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, CallbackQuery
from aiogram import F
from bot import bot

import core.handlers.basic
from ..utils.statesform import *
from ..keyboards.inline import reg_status
from core.database import *

reg_router = Router()


@reg_router.message(StateFilter(Registration.step_start_reg))
async def reg(message, state: FSMContext):
    await state.set_state(Registration.first_name)
    await message.answer(text='Введите имя:')


# Хэндлер на имя пользователя
@reg_router.message(StateFilter(Registration.first_name))
async def register_handler(message, state: FSMContext):
    await state.set_state(Registration.second_name)
    await state.update_data(first_name=message.text)
    await message.answer(text='Введите фамилию:')


# Хэндлер на фамилию пользователя
@reg_router.message(StateFilter(Registration.second_name))
async def register_handler(message, state: FSMContext):
    await state.update_data(second_name=message.text)
    await state.set_state(Registration.middle_name)
    await message.answer("Введите отчество:")


# Хэндлер на отчество пользователя
@reg_router.message(StateFilter(Registration.middle_name))
async def register_handler(message, state: FSMContext):
    await state.update_data(middle_name=message.text)
    await state.set_state(Registration.group)
    await message.answer('Введите учебнуюю групп в формате(СГН3-21Б):')


# Хэндлер на группу пользователя
@reg_router.message(StateFilter(Registration.group))
async def register_handler(message, state: FSMContext):
    await state.update_data(group=message.text)
    data = await state.get_data()
    await message.answer(
        text=f"Имя: {data['first_name']}\nФамилия: {data['second_name']}\nОтчество: {data['middle_name']}\nГруппа: {data['group']}",
        reply_markup=reg_status)


@reg_router.callback_query(F.data == 'confirm')
async def confirm_reg(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_info = user.User.create(first_name=data['first_name'],
                                 last_name=data['second_name'],
                                 middle_name=data['middle_name'],
                                 group=data['group'],
                                 telegram_id=call.from_user.id,
                                 role=role.Role.ADMIN)
    team_code = data['team_code']
    event_id = data['event_id']
    event_info = data['event_info']
    team_info = data.get('team_info')

    if team_code and event_info.type == eventtype.EventType.TEAM:
        join_info = user.User.join(user_info, event_id, team_code=team_code)
        await bot.send_message(chat_id=team_info.leader.telegram_id,
                               text=f"@{call.from_user.username} присоединился к Вашей команде на мероприятие {event_info.name}!")
        await call.message.answer(
            text=f"Вы присоединились к команде {team_info.leader.first_name} на мероприятие {event_info.name}!\n")
    elif event_info.type == eventtype.EventType.TEAM:
        created_team_info = user.User.create_team(user_info, event_id)[0]

        await call.message.answer(text=f"Вы присоединились к мероприятию {event_info.name}!\n"
                                       f"Ссылка на приглашение участников команды: https://t.me/fsgn_events_bot?start=event-{event_info.id}-team-{created_team_info.code}")
    else:
        user.User.join(user_info, event_id)
        await call.message.answer(text=f"Вы присоединились к мероприятию {event_info.name}!\n")

    await state.clear()


@reg_router.callback_query(F.data == 'change')
async def change_reg(call: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.first_name)
    await call.message.edit_text(text='Введите имя:', reply_markup=None)

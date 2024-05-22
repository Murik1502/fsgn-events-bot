from aiogram.filters import Command, StateFilter, state
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, CallbackQuery
from aiogram import F
from bot import bot
from cache.participants import participants
from ..utils.statesform import *
from ..keyboards.inline import reg_status
from core.database import *

reg_router = Router()


@reg_router.message(StateFilter(Registration.step_start_reg))
async def reg(message, state: FSMContext):
    await state.set_state(Registration.first_name)
    await message.answer(text='Введите Ваше Имя:')


# Хэндлер на имя пользователя
@reg_router.message(StateFilter(Registration.first_name))
async def register_handler(message, state: FSMContext):
    await state.set_state(Registration.second_name)
    await state.update_data(first_name=message.text.capitalize())
    await message.answer(text='Введите Вашу Фамилию:')


# Хэндлер на фамилию пользователя
@reg_router.message(StateFilter(Registration.second_name))
async def register_handler(message, state: FSMContext):
    await state.update_data(second_name=message.text.capitalize())
    await state.set_state(Registration.middle_name)
    await message.answer("Введите Ваше Отчество:")


# Хэндлер на отчество пользователя
@reg_router.message(StateFilter(Registration.middle_name))
async def register_handler(message, state: FSMContext):
    await state.update_data(middle_name=message.text.capitalize())
    await state.set_state(Registration.group)
    await message.answer(
        'Введите Вашу учебную группу в формате (СГН3-21Б)\n\nЕсли Вы не являетесь студентом МГТУ - введите "-"')


# Хэндлер на группу пользователя
@reg_router.message(StateFilter(Registration.group))
async def register_handler(message, state: FSMContext):
    await state.update_data(group=message.text)
    await state.update_data(message=message)
    data = await state.get_data()
    await message.answer(
        text=f"Проверьте введенные данные:\n\n"
             f"🔹Имя: {data['first_name']}\n🔹Фамилия: {data['second_name']}\n🔹Отчество: {data['middle_name']}\n🔹Группа: {data['group']}",
        reply_markup=reg_status)


@reg_router.callback_query(F.data == 'confirm')
async def confirm_reg(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    user_info = user.User.create(first_name=data['first_name'],
                                 last_name=data['second_name'],
                                 middle_name=data['middle_name'],
                                 group=data['group'],
                                 telegram_id=call.from_user.id,
                                 role=role.Role.DEFAULT)
    team_code = data.get('team_code')
    event_id = data.get('event_id')
    event_info = data.get('event_info')
    team_info = data.get('team_info')
    if event_id is None:
        await call.message.answer("Вы успешно зарегестрировались!")
    elif team_code and event_info.type == eventtype.EventType.TEAM:
        join_info = user.User.join(user_info, event_id, team_code=team_code, telegram_tag=call.from_user.username)

        # добавление в мапу
        participants.addParticipant(event_id=event_id, user_id=user_info.telegram_id)

        await bot.send_message(chat_id=team_info.leader.telegram_id,
                               text=f"@{call.from_user.username} присоединился к Вашей команде на мероприятие {event_info.name}!")
        await call.message.answer(
            text=f"Вы присоединились к команде {team_info.leader.first_name} на мероприятие {event_info.name}!\n")
    elif event_info.type == eventtype.EventType.TEAM:
        created_team_info = user.User.create_team(user_info, event_id, telegram_tag=call.from_user.username)[0]

        # добавление в мапу
        participants.addParticipant(event_id=event_id, user_id=user_info.telegram_id)

        await call.message.answer(text=f"Вы присоединились к мероприятию {event_info.name}!\n"
                                       f"Ссылка на приглашение участников команды:\n`https://t.me/fsgn_events_bot?start=event-{event_info.id}-team-{created_team_info.code}`",
                                  parse_mode="markdown")
    else:
        user.User.join(user_info, event_id, telegram_tag=call.from_user.username)

        # добавление в мапу
        participants.addParticipant(event_id=event_id, user_id=user_info.telegram_id)

        await call.message.answer(text=f"Вы присоединились к мероприятию {event_info.name}!\n")
    stateData = await state.get_data()
    print(stateData)
    message = stateData['message']
    func = stateData['start_func']
    await func(message, state)


@reg_router.callback_query(F.data == 'change')
async def change_reg(call: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.first_name)
    await call.message.edit_text(text='Введите имя:', reply_markup=None)

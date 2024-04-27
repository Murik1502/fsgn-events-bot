from aiogram.filters import Command, StateFilter, state
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, CallbackQuery

from google_sheet.sheet_editor import Sheet
from ..database import user, eventtype, role
from ..utils.statesform import *
from ..keyboards.inline import event_type, event_status
import datetime

admin_router = Router()


# Хэндлер на команду /new_event
@admin_router.message(Command('new_event'))
async def new_event(message, state: FSMContext):
    user_info = user.User.fetch_by_tg_id(message.from_user.id)
    if user_info.role != role.Role.ADMIN:
        return
    await state.set_state(CreateEvent.step_image)
    await state.update_data(id=1)
    await message.answer(text='Отправте картинку для мероприятия')


# Хэндлер на картинку для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_image))
async def register_handler(message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    print(message.photo[-1].file_id)
    await state.set_state(CreateEvent.step_name)
    await message.answer(text='Отправте название мероприятия')


# Хэндлер на название для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_name))
async def register_handler(message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateEvent.step2_description)
    await message.answer(text='Отправте описание к мероприятию')


# Хэндлер на описание для мероприятия
@admin_router.message(StateFilter(CreateEvent.step2_description))
async def register_handler(message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CreateEvent.step_type)
    await message.answer('Выберите тип мероприятия', reply_markup=event_type)


# Хэндлер на тип для мероприятия
@admin_router.callback_query(F.data == 'individual')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await state.set_state(CreateEvent.step_date)
    await call.message.edit_text("Вы выбрали одиночный тип мероприятия", reply_markup=None)
    await call.message.answer('Введите дату мероприятия(в формате 23.01.23):')


# Хэндлер на тип для мероприятия
@admin_router.callback_query(F.data == 'team')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await state.set_state(CreateEvent.step_date)
    await call.message.edit_text("Вы выбрали командный тип мероприятия", reply_markup=None)
    await call.message.answer('Введите дату мероприятия(в формате 23.01.23):')


# Хэндлер на дату для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_date))
async def register_handler(message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer('Введите время для мероприятия(в формате 12:30)')
    await state.set_state(CreateEvent.step_time)


# Хэндлер на время для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_time))
async def register_handler(message, state: FSMContext):
    data = await state.get_data()
    final_time = data['date'] + " " + message.text
    await state.update_data(date=final_time)
    data = await state.get_data()
    await message.answer_photo(data['image'],
                               caption=f"Название: {data['name']}\nДата проведения: {data['date']}\nОписание: {data['description']}\nТип мероприятия: {data['type']}",
                               reply_markup=event_status)


# Хэндлер для сохранения мероприятия
@admin_router.callback_query(F.data == 'add event')
async def type_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date_event = datetime.datetime.strptime(data['date'], "%d.%m.%y %H:%M")
    type_event = eventtype.EventType.DEFAULT
    user_info = user.User.fetch_by_tg_id(call.from_user.id)
    await call.message.edit_caption(
        caption=f"Название: {data['name']}\nДата проведения: {date_event}\nОписание: {data['description']}\nТип мероприятия: {data['type']}",
        reply_markup=None)
    msg = await call.message.answer('Пожалуйста, подождите...')
    if data['type'] == 'team':
        sheet = Sheet(data['name'], team=True)
        link = sheet.createSheet(['telegram_id', 'telegram_tag', 'ФИО', 'Группа', 'Команда', 'Подтвердил участие'],
                                 [['', '', '', '', '', '']])
    else:
        sheet = Sheet(data['name'], team=False)
        link = sheet.createSheet(['telegram_id', 'telegram_tag', 'ФИО', 'Группа', 'Подтвердил участие'],
                                 [['', '', '', '', '']])
    if data['type'] == 'team':
        type_event = eventtype.EventType.TEAM
    event_info = user.User.create_event(
        photo_id=data['image'],
        google_sheet=link,
        description=data['description'],
        type=type_event,
        date=date_event,
        name=data['name'],
        self=user_info
    )
    await msg.edit_text('Мероприятяие успешно создано. Ссылка-приглашение:\n'
                        f'https://t.me/fsgn_events_bot?start=event-{event_info.id}\n'
                        f'Ссылка на гугл-таблицу:\n'
                        f'{link}')


# Хэндлер на пересоздание мероприятия
@admin_router.callback_query(F.data == 'create again')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_caption(caption='Пожалуйста введите данные для этого мероприятия заново', reply_markup=None)
    await state.set_state(CreateEvent.step_image)
    await call.message.answer('Отправте картинку для мероприятия')

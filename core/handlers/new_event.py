from aiogram.filters import Command, StateFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot import bot

from cache.apsched import scheduler
from cache.apsched import mailing
from cache.participants import participants

from google_sheet.sheet_editor import Sheet
from ..database import user, eventtype, role, event
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
    if not message.photo:
        await state.update_data(name=message.text)
        await state.set_state(CreateEvent.step2_description)
        await message.answer(text='Отправте описание к мероприятию')


# Хэндлер на описание для мероприятия
@admin_router.message(StateFilter(CreateEvent.step2_description))
async def register_handler(message, state: FSMContext):
    if not message.photo:
        await state.update_data(description=message.text)
        await state.set_state(CreateEvent.step_type)
        await message.answer('Выберите тип мероприятия', reply_markup=event_type)


# Хэндлер на тип для мероприятия
@admin_router.callback_query(F.data == 'individual')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await state.set_state(CreateEvent.step_datetime)
    await call.message.edit_text("Вы выбрали одиночный тип мероприятия", reply_markup=None)
    await call.message.answer('Введите дату мероприятия(в формате 23.01.23):')


# Хэндлер на тип для мероприятия
@admin_router.callback_query(F.data == 'team')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await state.set_state(CreateEvent.step_datetime)
    await call.message.edit_text("Вы выбрали командный тип мероприятия", reply_markup=None)
    await call.message.answer('Введите дату и время мероприятия(в формате 00.00.00 00:00):')


# Хэндлер на дату и время для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_datetime))
async def register_handler(message, state: FSMContext):
    data = await state.get_data()
    if not message.photo:
        try:
            await state.update_data(date=datetime.datetime.strptime(message.text, "%d.%m.%y %H:%M"))
        except ValueError:
            await message.answer("Введите дату и время, предстоящего мероприятия в корректоном формате(например: "
                                 "00.00.00 00:00)")
        else:
            if datetime.datetime.now() > datetime.datetime.strptime(message.text, "%d.%m.%y %H:%M"):
                await message.answer(
                    "Дата должна быть позднее сегодняшнего дня!")
            else:
                data = await state.get_data()
                await message.answer_photo(data['image'],
                                           caption=f"Название: {data['name']}\nДата проведения: {data['date']}\nОписание: {data['description']}\nТип мероприятия: {data['type']}",
                                           reply_markup=event_status)


# Хэндлер для сохранения мероприятия
@admin_router.callback_query(F.data == 'add event')
async def type_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date_event = data['date']
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

    # ЗАГЛУШКА. ПОМЕНЯТЬ!!! В качестве переменной передавать время, за сколько до начала меро надо сделать рассылку
    time_step = datetime.timedelta(days=1)
    participants.addEvent(event_id=event_info.id)
    await scheduler.add_pending(bot=bot, func=mailing, date=date_event - time_step,
                                event_id=event_info.id)

    await msg.edit_text('Мероприятяие успешно создано. Ссылка-приглашение:\n'
                        f'https://t.me/fsgn_events_bot?start=event-{event_info.id}\n'
                        f'Ссылка на гугл-таблицу:\n'
                        f'{link}')


# Дописать, добавить текст сообщения и кнопки + их логику (придет/не придет)

# Хэндлер на пересоздание мероприятия
@admin_router.callback_query(F.data == 'create again')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_caption(caption='Пожалуйста введите данные для этого мероприятия заново', reply_markup=None)
    await state.set_state(CreateEvent.step_image)
    await call.message.answer('Отправте картинку для мероприятия')

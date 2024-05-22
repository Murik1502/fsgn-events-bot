from aiogram.filters import Command, StateFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot import bot

from cache.apsched import scheduler
from cache.apsched import mailing
from cache.participants import participants

from google_sheet.sheet_editor import Sheet
from ..database import user, eventtype, role, event, participant
from ..database.visit import Visit
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
    await message.answer(text='Отправьте афишу для мероприятия')


# Хэндлер на картинку для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_image))
async def register_handler(message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    print(message.photo[-1].file_id)
    await state.set_state(CreateEvent.step_name)
    await message.answer(text='Отправьте название мероприятия')


# Хэндлер на название для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_name))
async def register_handler(message, state: FSMContext):
    if not message.photo:
        await state.update_data(name=message.text)
        await state.set_state(CreateEvent.step2_description)
        await message.answer(text='Отправьте описание к мероприятию')


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
    await call.message.edit_text("Вы выбрали мероприятие с одиночным участием", reply_markup=None)
    await call.message.answer(
        f'Введите дату и время мероприятия в формате (15.06.24 12:30)')


# Хэндлер на тип для мероприятия
@admin_router.callback_query(F.data == 'team')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await state.set_state(CreateEvent.step_datetime)
    await call.message.edit_text("Вы выбрали командный тип мероприятия", reply_markup=None)
    await call.message.answer(
        f'Введите дату и время мероприятия в формате (15.06.24 12:30)')


# Хэндлер на дату и время для мероприятия
@admin_router.message(StateFilter(CreateEvent.step_datetime))
async def register_handler(message, state: FSMContext):
    data = await state.get_data()
    if not message.photo:
        try:
            await state.update_data(date=datetime.datetime.strptime(message.text, "%d.%m.%y %H:%M"))
        except ValueError:
            await message.answer(
                f'Введите дату и время в корректном формате (15.06.24 12:30)')
        else:
            if datetime.datetime.now() > datetime.datetime.strptime(message.text, "%d.%m.%y %H:%M"):
                await message.answer(
                    "Дата должна быть позже сегодняшнего дня!")
            else:
                data = await state.get_data()
                type = "командное"
                if data['type'] != 'team': type = 'одиночное'
                await message.answer_photo(data['image'],
                                           caption=f"Проверьте введеные данные:\n\n🔹Название:\n{data['name']}\n\n🔹Дата проведения:\n{data['date']}\n\n🔹Описание:\n{data['description']}\n\n🔹Тип мероприятия: {type}",
                                           reply_markup=event_status)


# Хэндлер для сохранения мероприятия
@admin_router.callback_query(F.data == 'add event')
async def type_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date_event = data['date']
    type_event = eventtype.EventType.DEFAULT
    user_info = user.User.fetch_by_tg_id(call.from_user.id)
    type = "командное"
    if data['type'] != 'team': type = 'одиночное'
    await call.message.edit_caption(
        caption=f"🔹Название:\n{data['name']}\n\n🔹Дата проведения:\n{data['date']}\n\n🔹Описание:\n{data['description']}\n\n🔹Тип мероприятия: {type}",
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

    time_step = datetime.timedelta(days=1)
    participants.addEvent(event_id=event_info.id)
    await scheduler.add_pending(bot=bot, func=mailing, date=date_event - time_step,
                                event_id=event_info.id)

    await msg.edit_text('Мероприятяие успешно создано.\nСсылка-приглашение:\n'
                        f'`https://t.me/fsgn_events_bot?start=event-{event_info.id}`\n'
                        f'Ссылка на гугл-таблицу:\n'
                        f'{link}', parse_mode="MARKDOWN")


@admin_router.callback_query(F.data.startswith('yes_visit'))
async def type_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Вы подтвердили свое участие')
    event_id = call.data[9:]
    for partic in user.User.fetch_by_tg_id(call.from_user.id).participation():
        if partic.event.id == int(event_id):
            participants.addParticipant(call.from_user.id, event_id)
            partic.visit = Visit.YES
            return


@admin_router.callback_query(F.data.startswith('no_visit'))
async def type_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Вы отказались принять участие')
    event_id = call.data[8:]
    for partic in user.User.fetch_by_tg_id(call.from_user.id).participation():
        if partic.event.id == int(event_id):
            participants.addParticipant(call.from_user.id, event_id)
            partic.visit = Visit.NO
            return


# Хэндлер на пересоздание мероприятия
@admin_router.callback_query(F.data == 'create again')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_caption(caption='Пожалуйста введите данные для этого мероприятия заново', reply_markup=None)
    await state.set_state(CreateEvent.step_image)
    await call.message.answer('Отправьте афишу для мероприятия')

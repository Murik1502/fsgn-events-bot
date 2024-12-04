import os

from aiogram.filters import Command, StateFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from bot import bot

from cache.apsched import scheduler
from cache.apsched import mailing
from cache.participants import participants

from google_sheet.sheet_editor import Sheet
from ..database import user, eventtype, role, event, participant, exceptions
from ..database.visit import Visit
from ..utils.statesform import *
from ..keyboards.inline import event_type, event_status, mail_type, mail_approve, image
import datetime


mail_router = Router()


# Хэндлер на команду /mailing
@mail_router.message(Command('mailing'))
async def mailing_handler(message, state: FSMContext):
    user_info = user.User.fetch_by_tg_id(message.from_user.id)
    if user_info.role != role.Role.ADMIN:
        return
    await message.answer(text='Сделать рассылку с картинкой?',reply_markup=image)

# Хэндлер на рассылку с картинкой
@mail_router.callback_query(F.data == 'with image')
async def mailing_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(None)
    await call.message.edit_text(text="Отправте картинку для рассылки")
    await state.set_state(MailStates.image_step)

# Хэндлер на рассылку без картинки
@mail_router.callback_query(F.data == 'without')
async def mailing_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(None)
    await call.message.edit_text(text="Отправте текст для рассылки")
    await state.set_state(MailStates.text_step)


# Хэндлер на картинку
@mail_router.message(StateFilter(MailStates.image_step))
async def image_handler(message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(MailStates.text_step)
    await message.answer(text='Отправте текст расслыки')


# Хэндлер на текст
@mail_router.message(StateFilter(MailStates.text_step))
async def text_handler(message, state: FSMContext):
    if not message.photo:
        await state.update_data(text=message.text)
        await state.set_state(MailStates.mail_type_step)
        await message.answer(text='Разослать сообщение всем пользователям или только участникам опредленного мероприятия?',reply_markup=mail_type)


# Хэндлер на тип рассылки для всех пользователй
@mail_router.callback_query(F.data == 'all users')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await state.set_state(MailStates.approve_step)
    await call.message.edit_text("Вы выбрали рассылку для всех пользователей", reply_markup=None)
    data = await state.get_data()
    try:
        image_info = data['image']
        await call.message.answer_photo(image=image_info,caption=f"{data['text']}\nРассылка предназначена для всех пользователей",reply_markup=mail_approve)
    except:
        await call.message.answer(text=f"{data['text']}\nРассылка предназначена для всех пользователей",reply_markup=mail_approve)


# Хэндлер на тип рассылки для участников определенного мероприятия
@mail_router.callback_query(F.data == 'only participants')
async def type_handler(call: CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await state.set_state(MailStates.chose_event)
    await call.message.edit_text("Вы выбрали рассылку для участников мероприятия", reply_markup=None)
    try:
        all_events = InlineKeyboardMarkup(inline_keyboard=[])
        for e in event.Event.fetch_all():
            all_events.inline_keyboard.append(
                [InlineKeyboardButton(text=f"{e.name} ({e.date.day}.{e.date.month}.{e.date.year})",
                                          callback_data=f"chose event {e.id}")])
        await call.message.answer(
            text="Выберите меропритие участникам которого необходимо отправить сообщение",
            reply_markup=all_events)
    except exceptions.EventNotFound:
        await call.message.answer("На данный момент нет активных мероприятий (")

# Хэндлер на опредленное мероприятие
@mail_router.callback_query(F.data.contains("chose event"))
async def event_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(None)
    await call.message.edit_text(f"Вы выбрали мероприятие: {event.Event.fetch(call.data[11:]).name}")
    await state.update_data(event=call.data[11:])
    await state.set_state(MailStates.approve_step)
    data = await state.get_data()
    try:
        await call.message.answer_photo(data['image'],
                                        caption=f"{data['text']}\n Отправить участникам мероприятия:{event.Event.fetch(data['event']).name}",
                                        reply_markup=mail_approve)
    except:
        await call.message.answer(text=f"{data['text']}\n Отправить участникам мероприятия:{event.Event.fetch(data['event']).name}",
                                        reply_markup=mail_approve)

# Хэндлер на подтверждение рассылки
@mail_router.callback_query(F.data.contains("mail"))
async def start_mail_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    if 'event' in data:
        e = event.Event.fetch(data['event'])
        p = e.participants()
    else:
        p = user.User.fetch_all()
    try:
        if 'image' in data:
            for model in p:
                user_id = model.user.telegram_id
                try:
                    await bot.send_photo(chat_id=user_id,
                                        photo=data['image'],
                                        caption=data['text'])
                except Exception as e:
                    print("something went wrong:", e)
        else:
            for model in p:
                user_id = model.user.telegram_id
                try:
                    await bot.send_message(chat_id=user_id,
                                           text=data['text'])
                except Exception as e:
                    print("something went wrong:", e)
    except exceptions.EventNotFound:
        print("Error: can't mailing, no such event")

# Хэндлер на пересоздание рассылки
@mail_router.callback_query(F.data.contains("recreate"))
async def create_mail_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await state.clear()
    await call.message.answer(text='Сделать рассылку с картинкой?',reply_markup=image)

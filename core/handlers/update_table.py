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
from ..database.event import Event
from ..database.visit import Visit
from ..utils.statesform import *
from ..keyboards.inline import event_type, event_status, mail_type, mail_approve, image
import datetime
import multiprocessing as mp
from cache.participants import participants as participants_map, update_limit


update_table_router = Router()

def run_update(sheet_obj, arg):
    sheet_obj.updateSheet(arg)


# Хэндлер на команду /update_table
@update_table_router.message(Command('update_table'))
async def update_table_handler(message, state: FSMContext):
    user_info = user.User.fetch_by_tg_id(message.from_user.id)
    if user_info.role != role.Role.ADMIN:
        return
    all_events = InlineKeyboardMarkup(inline_keyboard=[])
    events = event.Event.fetch_all()
    for e in events:
        if e.date.date() >= datetime.date.today():
            all_events.inline_keyboard.append(
                [InlineKeyboardButton(text=f"{e.name} ({e.date.day}.{e.date.month}.{e.date.year})",
                                      callback_data=f"update table{e.id}")])
    if len(all_events.inline_keyboard) == 0:
        raise exceptions.EventNotFound
    await message.answer("Выберите мероприятие для которого необходимо обновить таблицу",reply_markup=all_events)

@update_table_router.callback_query(F.data.startswith("update table"))
async def chose_event_handler(call: CallbackQuery):

    e = Event.fetch(int(call.data[len("update table"):]))
    if e.type == eventtype.EventType.TEAM:
        a = Sheet(e.name, True, link=e.google_sheet)
        allParticipants = e.participants()
        arr = []
        teams = []
        for p in allParticipants:
            if p.team.code not in teams:
                teams.append(p.team.code)
            if p.visit.value == 0:
                visit = ''
            elif p.visit.value == -1:
                visit = 'Нет'
            else:
                visit = 'Да'
            arr.append([p.user.telegram_id, p.telegram_tag,
                        f"{p.user.last_name} {p.user.first_name} {p.user.middle_name}",
                        p.user.group, teams.index(p.team.code) + 1, visit])
        sheet_process = mp.Process(target=run_update, args=(a, arr))
        sheet_process.start()
        # Зачистка списка новозарегестрированных
        participants_map.clear(e.id)
    else:
        a = Sheet(e.name, False, link=e.google_sheet)
        allParticipants = e.participants()
        arr = []
        for p in allParticipants:
            if p.visit.value == 0:
                visit = ''
            elif p.visit.value == -1:
                visit = 'Нет'
            else:
                visit = 'Да'
            arr.append([p.user.telegram_id, p.telegram_tag,
                        f"{p.user.last_name} {p.user.first_name} {p.user.middle_name}",
                        p.user.group, visit])
        sheet_process = mp.Process(target=run_update, args=(a, arr))
        sheet_process.start()

    await call.message.edit_text(f"Таблица обновлена.\n{e.google_sheet}")

import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Callable
from aiogram import Bot
import datetime
from core.database import event, eventtype, exceptions
from defaults.settings import settings
from google_sheet.sheet_editor import Sheet
from cache.participants import participants as participants_map, update_limit


class Scheduler:
    """
    Класс для управления шедулером приложения

    атрибут sched: асинхронный шедулер с временной зоной МСК

    метод add_periodic: добавление функции, которая будет выполняться периодично с интервалом в секундах
    метод add_pending: добавление функции, которая будет выполнена в определённый момент времени

    При необходимости добавлять функции вручную аналогичным образом через
        scheduler.sched.add_job( *ссылка на функцию* , trigger='interval', seconds=*колличество секунд* ) - периодичную
        scheduler.sched.add_job( *ссылка на функцию*, trigger='date', next_run_time=*дата и время* ) - отложенную
    """

    def __init__(self):
        self.sched = AsyncIOScheduler(timezone="Europe/Moscow")

    async def add_periodic(self, bot: Bot, func: Callable, interval: int = 60):
        self.sched.add_job(func, trigger='interval', seconds=interval, kwargs={'bot': bot})

    async def add_pending(self, bot: Bot, func: Callable, date, **kwargs):
        print(kwargs, kwargs['event_id'])
        self.sched.add_job(func, trigger='date', next_run_time=date,
                           kwargs={'bot': bot, 'event_id': kwargs['event_id']})


scheduler = Scheduler()


async def mailing(bot: Bot, event_id) -> None:
    try:
        e = event.Event.fetch(event_id)
        p = e.participants()
        for model in p:
            user_id = model.user.telegram_id
            print(f"sending mail to {user_id}")
            visit_status = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Да", callback_data=f"yes_visit{event_id}"),
                 InlineKeyboardButton(text="Нет", callback_data=f"no_visit{event_id}")]
            ], )
            try:
                await bot.send_message(chat_id=user_id,
                                       reply_markup=visit_status,
                                       text=f"""Подтвердите свое участие в мероприятии "{e.name}" """)
                print("mail sent successfully!")
            except Exception as e:
                print("something went wrong:", e)
    except exceptions.EventNotFound:
        print("Error: can't mailing, no such event")

async def sheet(bot: Bot):
    try:
        events = event.Event.fetch_all()
    except exceptions.EventNotFound:
        return
    for e in events:
        if e.date.date() >= datetime.date.today() and int(participants_map.getCount(event_id=e.id)) >= update_limit:
            try:
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
                    a.updateSheet(arr)
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
                    a.updateSheet(arr)
                    # Зачистка списка новозарегестрированных
                    participants_map.clear(e.id)
            except Exception as e:
                print(e)
                pass
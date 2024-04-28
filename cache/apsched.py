import os

from aiogram import Bot
import datetime
from core.database import event, eventtype, exceptions
from google_sheet.sheet_editor import Sheet


async def periodic(bot: Bot):
    pass


async def sheet(bot: Bot):
    try:
        events = event.Event.fetch_all()
    except exceptions.EventNotFound:
        return
    for e in events:
        if e.date < datetime.datetime.now():
            try:
                if e.type == eventtype.EventType.TEAM:
                    a = Sheet(e.name, True, link=e.google_sheet)
                    participants = e.participants()
                    arr = []
                    teams = []
                    for p in participants:
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
                else:
                    a = Sheet(e.name, False, link=e.google_sheet)
                    participants = e.participants()
                    arr = []
                    for p in participants:
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
            except Exception as e:
                print(e)
                pass
    pass

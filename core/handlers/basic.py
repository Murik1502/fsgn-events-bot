import datetime
from bot import bot
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext

from ..utils.statesform import *
from ..keyboards.inline import *
from ..handlers.registration import *
from core.database import *

router = Router()


# Хэндлер на команду /start
@router.message(Command("start"))
async def start_handler(message, state: FSMContext):
    cmd = message.text.split()
    if len(cmd) == 2:
        parts = cmd[1].split("-")
        cmd_dict = {}
        for i in range(0, len(parts), 2):
            cmd_dict[parts[i]] = parts[i + 1]
        event_id = cmd_dict.get('event')
        team_code = cmd_dict.get('team')
        print(event_id, team_code)
        try:
            event_info = event.Event.fetch(event_id)
            if team_code:
                team_info = team.Team.fetch_by_code(team_code)
                await state.update_data(team_info=team_info)
                if team_info.event.id != event_info.id:
                    raise exceptions.TeamAnotherEvent

            try:
                user_info = user.User.fetch_by_tg_id(message.from_user.id)
                try:
                    if team_code and event_info.type == eventtype.EventType.TEAM:
                        join_info = user.User.join(user_info, event_id, team_code=team_code)
                        await bot.send_message(chat_id=team_info.leader.telegram_id,
                                               text=f"@{message.from_user.username} присоединился к Вашей команде на мероприятие {event_info.name}!")
                        await message.answer(
                            text=f"Вы присоединились к команде {team_info.leader.first_name} на мероприятие {event_info.name}!\n")
                    elif event_info.type == eventtype.EventType.TEAM:
                        created_team_info = user.User.create_team(user_info, event_id)[0]

                        await message.answer(text=f"Вы присоединились к мероприятию {event_info.name}!\n"
                                                  f"Ссылка на приглашение участников команды: https://t.me/fsgn_events_bot?start=event-{event_info.id}-team-{created_team_info.code}")
                    else:
                        user.User.join(user_info, event_id)
                        await message.answer(text=f"Вы присоединились к мероприятию {event_info.name}!\n")

                except exceptions.UserAlreadyJoined:
                    await message.answer(text=f"Вы уже присоединились к мероприятию {event_info.name}")

            except exceptions.UserNotFound:
                await state.update_data(event_id=event_id, team_code=team_code, event_info=event_info)
                await reg(message=message, state=state)

        except exceptions.EventNotFound or exceptions.TeamNotFound or exceptions.TeamAnotherEvent:
            await message.answer(text="Ссылка недействительна")

    else:
        for e in event.Event.fetch_all():
            print(e.name, e.type, e.date, e.google_sheet, e.photo_id, e.description)

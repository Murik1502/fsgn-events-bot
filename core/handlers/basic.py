import datetime
import os.path

from cache.participants import participants
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from bot import bot
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext

from .new_event import mailing
from ..utils.statesform import *
from ..handlers.registration import *
from core.database import *

router = Router()


# Хэндлер на команду /start
@router.message(Command("start"))
async def start_handler(message, state: FSMContext):
    await state.clear()
    cmd = message.text.split()
    if len(cmd) == 2:
        try:
            parts = cmd[1].split("-")
            cmd_dict = {}
            for i in range(0, len(parts), 2):
                cmd_dict[parts[i]] = parts[i + 1]
            event_id = cmd_dict.get('event')
            team_code = cmd_dict.get('team')

            event_info = event.Event.fetch(event_id)
            if event_info.date.date() < datetime.date.today():
                raise exceptions.EventOutOfDate
            if team_code:
                team_info = team.Team.fetch_by_code(team_code)
                await state.update_data(team_info=team_info)
                if team_info.event.id != event_info.id:
                    raise exceptions.TeamAnotherEvent

            try:
                user_info = user.User.fetch_by_tg_id(message.from_user.id)
                try:
                    if team_code and event_info.type == eventtype.EventType.TEAM:

                        participants.addParticipant(user_id=message.from_user.id, event_id=event_id)

                        join_info = user.User.join(user_info, event_id, team_code=team_code,
                                                   telegram_tag=message.from_user.username)
                        await bot.send_message(chat_id=team_info.leader.telegram_id,
                                               text=f"@{message.from_user.username} присоединился к Вашей команде на мероприятие {event_info.name}!")
                        await message.answer(
                            text=f"Вы присоединились к команде {team_info.leader.first_name} на мероприятие {event_info.name}!\n")
                    elif event_info.type == eventtype.EventType.TEAM:

                        participants.addParticipant(user_id=message.from_user.id, event_id=event_id)

                        created_team_info = user.User.create_team(user_info, event_id, message.from_user.username)
                        await message.answer(text=f"Вы присоединились к мероприятию {event_info.name}!\n"
                                                  f"Ссылка на приглашение участников команды: https://t.me/fsgn_events_bot?start=event-{event_info.id}-team-{created_team_info[0].code}")
                    else:
                        user.User.join(user_info, event_id, telegram_tag=message.from_user.username)
                        await message.answer(text=f"Вы присоединились к мероприятию {event_info.name}!\n")
                        participants.addParticipant(user_id=message.from_user.id, event_id=event_id)

                except exceptions.UserAlreadyJoined:
                    await message.answer(text=f"Вы уже присоединились к мероприятию {event_info.name}")

            except exceptions.UserNotFound:
                await state.update_data(event_id=event_id, team_code=team_code, event_info=event_info)
                await reg(message=message, state=state)

        except (IndexError, exceptions.EventNotFound, exceptions.TeamNotFound, exceptions.TeamAnotherEvent):
            await message.answer(text="Ссылка недействительна")
        except exceptions.EventOutOfDate:
            await message.answer(text=f"Мероприятие уже закончилось (")

    else:
        try:
            user_info = user.User.fetch_by_tg_id(message.from_user.id)
            try:
                all_events = InlineKeyboardMarkup(inline_keyboard=[])
                for e in event.Event.fetch_all():
                    if e.date.date() >= datetime.date.today():
                        all_events.inline_keyboard.append(
                            [InlineKeyboardButton(text=f"{e.name}(пройдет {e.date.day}.{e.date.month}.{e.date.year})",
                                                  callback_data=f"more info {e.id}")])
                if len(all_events.inline_keyboard) == 0:
                    raise exceptions.EventNotFound
                await message.answer_photo(
                    photo=FSInputFile(os.path.join(os.getcwd(), "core/static/welcom_image.png")),
                    caption="Добро пожаловать в бот для регистрации на мероприятия!\nВы можете выбрать и зарегистрироваться на мерпиятия из списка ниже",
                    reply_markup=all_events)
            except exceptions.EventNotFound:
                await message.answer("На данный момент нет активных мероприятий (")
        except exceptions.UserNotFound:
            await reg(message, state)


@router.callback_query(F.data.contains("more info"))
async def more_info(call: CallbackQuery):
    event_id = call.data.split()[2]
    data = event.Event.fetch(int(event_id))
    type_event = "Командное"
    if data.type == eventtype.EventType.DEFAULT:
        type_event = "Одиночное"
    join_event = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вступить", url=f'https://t.me/fsgn_events_bot?start=event-{data.id}'), ],
        [InlineKeyboardButton(text="Вернуться назад", callback_data='go back'), ]
    ], )
    try:
        await call.message.edit_media(media=InputMediaPhoto(media=data.photo_id,
                                                            caption=f"Название: {data.name}\nДата проведения: {data.date}\nОписание: {data.description}\nТип мероприятия: {type_event}"),
                                      reply_markup=join_event)
    except:
        await call.message.answer("fffffff")


@router.callback_query(F.data.contains("go back"))
async def go_back(call: CallbackQuery):
    try:
        all_events = InlineKeyboardMarkup(inline_keyboard=[])
        events = event.Event.fetch_all()
        for e in events:
            if e.date.date() >= datetime.date.today():
                all_events.inline_keyboard.append(
                    [InlineKeyboardButton(text=f"{e.name}(пройдет {e.date.day}.{e.date.month}.{e.date.year})",
                                          callback_data=f"more info {e.id}")])
        if len(all_events.inline_keyboard) == 0:
            raise exceptions.EventNotFound
        photo = InputMediaPhoto(media=FSInputFile(os.path.join(os.getcwd(), "core/static/welcom_image.png")),
                                caption="Добро пожаловать в бот для регистрации на мероприятия!\nВы можете выбрать и зарегистрироваться на мерпиятия из списка ниже")
        await call.message.edit_media(media=photo,
                                      reply_markup=all_events)
    except exceptions.EventNotFound:
        await call.message.answer("На данный момент нет активных мероприятий (")

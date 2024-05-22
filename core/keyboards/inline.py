from aiogram.types import *

join_event = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Вступить", callback_data="event_id"),
     ]
], )

event_status = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сохранить", callback_data="add event"),
     InlineKeyboardButton(text="Пересоздать", callback_data="create again")]
], )

event_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Командное", callback_data="team"),
     InlineKeyboardButton(text="Одиночное", callback_data="individual")]
], )

reg_status = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Всё верно", callback_data="confirm"),
     InlineKeyboardButton(text="Изменить", callback_data="change")]
], )

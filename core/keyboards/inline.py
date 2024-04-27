from aiogram.types import *

join_event = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Вступить", callback_data="event_id"),
     ]
], )

reg_status = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Всё верно", callback_data="confirm"),
     InlineKeyboardButton(text="Изменить", callback_data="change")]
], )

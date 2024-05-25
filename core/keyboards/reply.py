from aiogram.types import *

admin_keyword = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/new_event",)],
    [KeyboardButton(text="/to_excel",)]
], resize_keyboard=True)
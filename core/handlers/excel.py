import datetime
import os.path

import xlsxwriter as xlsxwriter
from core.database import role
from ..handlers.registration import *
from core.database import *

exel_router = Router()


# Хэндлер на команду /to_exel
@exel_router.message(Command('to_excel'))
async def new_event(call: CallbackQuery):
    user_info = user.User.fetch_by_tg_id(call.from_user.id)
    if user_info.role != role.Role.ADMIN:
        return
    title = ["ФИО", "Тэг в тг", "Уровень доступа", "Учебная группа"]
    workbook = xlsxwriter.Workbook(os.path.join(os.getcwd(), "core/static/Users.xlsx"))
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})

    for i, col_name in enumerate(title): worksheet.write(0, i, col_name, bold)
    counter = 1
    for i in user.User.fetch_all():
        worksheet.write(counter, 0, f"{i.first_name} {i.last_name} {i.middle_name}")
        worksheet.write(counter, 1, i.telegram_id)
        user_role = "админ"
        if i.role != "admin": user_role = "Обычный пользователь"
        worksheet.write(counter, 2, user_role)
        worksheet.write(counter, 3, i.group)
        counter += 1
    worksheet.autofit()
    workbook.close()
    await call.answer_document(FSInputFile(os.path.join(os.getcwd(), "core/static/Users.xlsx")))

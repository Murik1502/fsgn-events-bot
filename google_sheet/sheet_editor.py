import pandas as pd
from settings import client

def number_to_letter(df):
    number = len(df.columns)
    result = ''
    while number > 0:
        number -= 1
        result = chr(65 + (number % 26)) + result
        number //= 26
    return result


def style_sheet(worksheet, df):
    worksheet.format(f'A1:{number_to_letter(df)}1', {
        "backgroundColor": {
            "red": 0.7529,
            "green": 0.9137,
            "blue": 0.7529
        },
        "borders": {
            "bottom": {
                "style": "SOLID",
                "width": 2,
                "color": {"red": 0, "green": 0, "blue": 0}
            }
        },
        "textFormat": {
            "fontSize": 12,
            "bold": True
        }
    })
    worksheet.format(f'{chr(ord(number_to_letter(df)) + 1)}1:{chr(ord(number_to_letter(df)) + 1)}{len(df) + 1}', {
        "backgroundColor": {
            "red": 1.0,
            "green": 1.0,
            "blue": 1.0
        },
        "borders": {
            "left": {
                "style": "SOLID",
                "width": 2,
                "color": {"red": 0, "green": 0, "blue": 0}
            },
        },
        "textFormat": {
            "fontSize": 12,
            "bold": True
        }
    })

    worksheet.format(f'A{len(df) + 2}:{chr(ord(number_to_letter(df)))}{len(df) + 2}', {
        "backgroundColor": {
            "red": 1.0,
            "green": 1.0,
            "blue": 1.0
        },
        "borders": {
            "top": {
                "style": "SOLID",
                "width": 2,
                "color": {"red": 0, "green": 0, "blue": 0}
            },
        },
        "textFormat": {
            "fontSize": 12,
            "bold": True
        }
    })


class Sheet:
    """
                Класс для управления таблицами Google Sheets. Позволяет создавать, обновлять и модифицировать
                таблицы, а также управлять доступом к ним.

                Атрибуты:
                    tableName (str): Название таблицы в Google Sheets.

                    team (bool): Определяет, будут ли в мероприятии разделение на команды.

                    link (str, optional): Ссылка на созданную таблицу Google Sheets. Если создаете таблицу в первый раз, то не отмечайте поле.


                    Поле link нужно если вы хотите обратиться к уже созданной таблице по link из БД
                """

    def __init__(self, tableName: str, team: bool, link=None) -> None:
        """
                    Класс для управления таблицами Google Sheets. Позволяет создавать, обновлять и модифицировать
                    таблицы, а также управлять доступом к ним.

                    Атрибуты:
                        tableName (str): Название таблицы в Google Sheets.

                        team (bool): Определяет, будут ли в мероприятии разделение на команды.

                        link (str, optional): Ссылка на созданную таблицу Google Sheets. Если создаете таблицу в первый раз, то не отмечайте поле.


                        Поле link нужно если вы хотите обратиться к уже созданной таблице по link из БД
                    """
        self.tableName = tableName
        self.team = team
        self.link = link

    def createSheet(self, title: list[str], data: list[list[str]]) -> str:
        """
                Создает новую таблицу в Google Sheets, заполняет ее данными и возвращает ссылку на нее.

                Параметры:
                    title (list[str]): Список заголовков столбцов для новой таблицы.

                    data (list[list[str]]): Данные для заполнения таблицы в формате списка списков.

                Возвращает:
                    str: Ссылка на созданную таблицу Google Sheets.
                """
        sheet = client.create(self.tableName)
        self.link = sheet.url
        sheet.share(None, perm_type='anyone', role='writer')
        worksheet = client.open_by_url(self.link).sheet1

        df = pd.DataFrame(data, columns=title)
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        style_sheet(worksheet, df)

        if self.team:
            df.sort_values(by='Команда', inplace=True)
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            last_indices = df[df['Команда'] != df['Команда'].shift(-1)].index.tolist()
            for index in last_indices:
                worksheet_index = index + 2
                worksheet.format(f"A{worksheet_index}:{number_to_letter(df)}{worksheet_index}", {
                    "borders": {
                        "bottom": {
                            "style": "SOLID",
                            "width": 1,
                            "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}
                        }
                    }
                })

        style_sheet(worksheet, df)

        return self.link

    def updateSheet(self, data=None) -> list[str]:
        """
                Обновляет содержимое таблицы в Google Sheets. Если данные не предоставлены, возвращает
                текущие заголовки таблицы.

                Параметры:
                    data (list[list[str]], optional): Данные для обновления таблицы. Если None, метод
                    возвращает заголовки текущей таблицы.

                Возвращает:
                    list[str]: Список заголовков, если не предоставлены данные для обновления.
                """
        worksheet = client.open_by_url(self.link).sheet1
        if data is None:
            return worksheet.row_values(1)
        else:
            sheetData = worksheet.get_all_values()
            df = pd.DataFrame(sheetData[1:], columns=sheetData[0])
            new_data_df = pd.DataFrame(data, columns=df.columns)
            df = pd.concat([df, new_data_df], ignore_index=True)
            df.sort_values(by='Команда', inplace=True)  # Пересортировка после добавления новых данных
            worksheet.clear()
            requests = [{
                "updateCells": {
                    "range": {
                        "sheetId": worksheet._properties['sheetId'],
                        "startRowIndex": 0,
                        "endRowIndex": 1000,
                        "startColumnIndex": 0,
                        "endColumnIndex": 30
                    },
                    "fields": "userEnteredFormat"
                }
            }]

            worksheet.spreadsheet.batch_update({'requests': requests})
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())

            if self.team:
                last_indices = df[df['Команда'] != df['Команда'].shift(-1)].index.tolist()
                for index in last_indices:
                    worksheet_index = index + 2
                    worksheet.format(f"A{worksheet_index}:{number_to_letter(df)}{worksheet_index}", {
                        "borders": {
                            "bottom": {
                                "style": "SOLID",
                                "width": 1,
                                "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}
                            }
                        }
                    })
            style_sheet(worksheet, df)

    def deleteUsers(self, users: list, id=0) -> None:
        """
               Удаляет строки в таблице, соответствующие ID пользователям из предоставленного списка.
               ID поумолчанию в первой колонке.

               Параметры:
                   users (list[str|int]): Список ID пользователей, чьи данные следует удалить из таблицы.

                   id (int): Индекс столбца, в котором хранятся ID пользователей. По умолчанию стоит 0
               Очищает все форматы и обновляет данные, оставляя только те строки, которые не включают указанные ID.
               """
        try:
            users = map(int, users)
        except:
            pass
        worksheet = client.open_by_url(self.link).sheet1
        sheetData = worksheet.get_all_values()
        df = pd.DataFrame(sheetData[1:], columns=sheetData[0])
        mask = ~(df.iloc[:, id]).isin(users)
        df = df[mask].reset_index(drop=True)
        worksheet.clear()

        requests = [{
            "updateCells": {
                "range": {
                    "sheetId": worksheet._properties['sheetId'],
                    "startRowIndex": 0,
                    "endRowIndex": 1000,
                    "startColumnIndex": 0,
                    "endColumnIndex": 30
                },
                "fields": "userEnteredFormat"
            }
        }]
        worksheet.spreadsheet.batch_update({'requests': requests})
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

        if self.team:
            last_indices = df[df['Команда'] != df['Команда'].shift(-1)].index.tolist()
            for index in last_indices:
                worksheet_index = index + 2
                worksheet.format(f"A{worksheet_index}:{number_to_letter(df)}{worksheet_index}", {
                    "borders": {
                        "bottom": {
                            "style": "SOLID",
                            "width": 1,
                            "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}
                        }
                    }
                })

        style_sheet(worksheet, df)


"""Для работы с Google Sheets необходимо установить библиотеку необходимо в requirements.txt установить oauth2client, 
gspread, pandas, peewee

Для начала работы с Google Sheets пропишите следующеее

from google_sheets import Sheet

Далее смотри пример использование класса и документацию по классу
Пример:
a = Sheet('Test1', True)
print(a.createSheet(['id', 'Имя', 'Группа', 'Команда'],
                    [['1', 'Максим', '23', '1'], ['4', 'Ильдар', '23', '1'], ['7', 'Влад', '24', '2'],
                     ['10', 'Алексей', '22', '3']]))
a.updateSheet([['15', 'Маша', '12', '3']])
a.deleteUsers(['4'], 0)
"""

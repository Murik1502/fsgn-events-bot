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
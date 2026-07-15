from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from utils.misc import commands, cities

set_timezone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=commands.get('send_location'), request_location=True)],
        [KeyboardButton(text=commands.get('choose_city'))],
        [KeyboardButton(text=commands.get('choose_timezone'))],
        [KeyboardButton(text=commands.get('use_utc'))],
        [KeyboardButton(text=commands.get('cancel'))],
    ],
    resize_keyboard=True,
)

choose_city_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=cities.get('Moscow')),
         KeyboardButton(text=cities.get('Yekaterinburg'))],
        [KeyboardButton(text=cities.get('Yerevan')),
         KeyboardButton(text=cities.get('Tbilisi'))],
        [KeyboardButton(text=cities.get('Minsk')),
         KeyboardButton(text=cities.get('no_city'))],
        [KeyboardButton(text=commands.get('cancel'))],
    ],
    resize_keyboard=True,
)

confirm_create_reminder_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=commands.get('create')),
         KeyboardButton(text=commands.get('cancel'))],
    ],
    resize_keyboard=True,
)

confirm_delete_reminder_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=commands.get('delete')),
         KeyboardButton(text=commands.get('cancel'))]
    ],
    resize_keyboard=True,
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=commands.get('cancel'))]],
    resize_keyboard=True,
)
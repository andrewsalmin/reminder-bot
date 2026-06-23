import logging
from zoneinfo import available_timezones

import asyncpg
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from timezonefinder import TimezoneFinder

from keyboards import keyboards
from utils.db import create_or_update_user, update_timezone
from utils.misc import commands, cities, timezones

router = Router()
logger = logging.getLogger(__name__)

class TimezoneSetupStates(StatesGroup):
    waiting_for_timezone_setting_method = State()
    waiting_for_location = State()
    waiting_for_city = State()
    waiting_for_timezone_query = State()
    waiting_for_timezone_choice = State()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    try:
        await state.clear()

        await create_or_update_user(message, conn)

        await message.answer(
            'Привет! 👋\n'
            'Чтобы я отправлял напоминания в твоём местном времени, выбери один из вариантов:\n\n',
            reply_markup=keyboards.set_timezone_kb,
        )

        await state.set_state(TimezoneSetupStates.waiting_for_timezone_setting_method)

    except Exception as e:
        logger.exception('Ошибка обращения к пользователю: %s.', e)
        await message.answer(
            'Ошибка обращения к пользователю 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )

@router.message(StateFilter(None), Command('set_timezone'))
async def set_timezone(message: Message, state: FSMContext) -> None:
    await message.answer(
        'Чтобы изменить часовой пояс, выбери один из вариантов:\n\n',
        reply_markup=keyboards.set_timezone_kb,
    )

    await state.set_state(TimezoneSetupStates.waiting_for_timezone_setting_method)

@router.message(TimezoneSetupStates.waiting_for_timezone_setting_method)
async def handle_user_choice(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    if message.location:
        try:
            lat = message.location.latitude
            lon = message.location.longitude
            timezone = TimezoneFinder().timezone_at(lat=lat, lng=lon) or 'UTC'

            await update_timezone(message.from_user.id, timezone, conn)

            await message.answer(
                f'Установлен часовой пояс: {timezone} ✅\n'
                'Напоминания будут работать по этому времени 🕓',
                reply_markup=ReplyKeyboardRemove(),
            )

            await state.clear()

        except Exception as e:
            logger.exception('Ошибка определения часового пояса: %s.', e)
            await message.answer(
                'Ошибка определения часового пояса 🛑 Попробуй позже',
                reply_markup=ReplyKeyboardRemove(),
            )

            await state.clear()

    elif message.text == commands.get('choose_city'):
        await message.answer(
            'Выбери город:',
            reply_markup=keyboards.choose_city_kb,
        )

        await state.set_state(TimezoneSetupStates.waiting_for_city)

    elif message.text == commands.get('choose_timezone'):
        await message.answer(
            'Введи часть названия часового пояса, например, `Europe` или `Asia`:',
            reply_markup=ReplyKeyboardRemove(),
        )

        await state.set_state(TimezoneSetupStates.waiting_for_timezone_query)

    elif message.text == commands.get('use_utc'):
        try:
            await update_timezone(message.from_user.id, 'UTC', conn)

            await message.answer(
                f'Установлен часовой пояс: UTC ✅\n'
                'Напоминания будут работать по этому времени 🕓',
                reply_markup=ReplyKeyboardRemove(),
            )

            await state.clear()

        except Exception as e:
            logger.exception('Ошибка установки часового пояса: %s.', e)
            await message.answer(
                'Ошибка установки часового пояса 🛑 Попробуй позже',
                reply_markup=ReplyKeyboardRemove(),
            )

            await state.clear()

    else:
        await message.answer(
            'Выбери один из вариантов на клавиатуре ⚠️',
        )

@router.message(TimezoneSetupStates.waiting_for_city)
async def handle_city_choice(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    try:
        city = message.text.strip()

        if city not in cities.values():
            await message.answer(
                'Выбери один из вариантов на клавиатуре ⚠️',
            )
            return

        city_tz_map = {
            cities.get('Moscow'): 'Europe/Moscow',
            cities.get('Yekaterinburg'): 'Asia/Yekaterinburg',
            cities.get('Yerevan'): 'Asia/Yerevan',
            cities.get('Tbilisi'): 'Asia/Tbilisi',
            cities.get('Minsk'): 'Europe/Minsk',
            cities.get('no_city'): 'UTC',
        }

        timezone = city_tz_map.get(city)

        await update_timezone(message.from_user.id, timezone, conn)

        await message.answer(
            f'Установлен часовой пояс: {timezone} ✅\n'
            'Напоминания будут работать по этому времени 🕓',
            reply_markup=ReplyKeyboardRemove(),
        )

        await state.clear()

    except Exception as e:
        logger.exception('Ошибка установки часового пояса: %s.', e)
        await message.answer(
            'Ошибка установки часового пояса 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )

        await state.clear()

@router.message(TimezoneSetupStates.waiting_for_timezone_query, F.text)
async def find_timezones(message: Message, state: FSMContext) -> None:
    query = message.text.strip().lower()
    matches = [tz for tz in sorted(available_timezones()) if query in tz.lower()]

    if not matches:
        await message.answer(
            'Cовпадений не найдено 😕\nПопробуй другую часть названия часового пояса',
        )
        return

    rows = []
    for i in range(0, len(matches), 2):
        row = [KeyboardButton(text=matches[i])]
        if i + 1 < len(matches):
            row.append(KeyboardButton(text=matches[i + 1]))
        rows.append(row)
    if len(matches) % 2 == 0:
        rows.append([KeyboardButton(text=timezones.get('no_timezone')), KeyboardButton(text=commands.get('cancel'))])
    else:
        rows[-1].append(KeyboardButton(text=timezones.get('no_timezone')))
        rows.append([KeyboardButton(text=commands.get('cancel'))])

    choose_timezone_kb = ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
    )

    await message.answer(
        'Выбери один из найденных часовых поясов:',
        reply_markup=choose_timezone_kb,
    )

    await state.update_data(timezone_matches=matches)
    await state.set_state(TimezoneSetupStates.waiting_for_timezone_choice)

@router.message(TimezoneSetupStates.waiting_for_timezone_choice, F.text)
async def save_timezone(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    try:
        timezone = message.text.strip()

        data = await state.get_data()
        timezone_matches = data.get('timezone_matches')

        if timezone not in timezone_matches and timezone not in timezones.values():
            await message.answer(
                'Выбери один из вариантов на клавиатуре ⚠️',
            )
            return

        if timezone == timezones.get('no_timezone'):
            timezone = 'UTC'

        await update_timezone(message.from_user.id, timezone, conn)

        await message.answer(
            f'Установлен часовой пояс: {timezone} ✅\n'
            'Напоминания будут работать по этому времени 🕓',
            reply_markup=ReplyKeyboardRemove(),
        )

        await state.clear()

    except Exception as e:
        logger.exception('Ошибка установки часового пояса: %s.', e)
        await message.answer(
            'Ошибка установки часового пояса 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )

        await state.clear()
import logging
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import asyncpg
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards import keyboards
from utils.db import add_user_reminder, get_user, get_user_reminders
from utils.misc import commands
from utils.misc import reminder_creation_message_example
from utils.reminder_parser import parse_reminder_input

router = Router()
logger = logging.getLogger(__name__)

class MainStates(StatesGroup):
    waiting_for_create_confirmation = State()

@router.message(StateFilter(None), Command('show_all_reminders'))
async def show_reminders(message: Message, conn: asyncpg.Connection) -> None:
    try:
        user = await get_user(message.from_user.id, conn)
        reminders = await get_user_reminders(user['id'], conn)

        if reminders:
            lines = []
            for reminder in reminders:
                remind_at = reminder['remind_at'].replace(tzinfo=timezone.utc).astimezone(ZoneInfo(user['timezone'] or 'UTC'))
                lines.append(f'#{reminder['id']} | 📅 {remind_at:%d.%m.%Y %H:%M} — {reminder['text']}')
            reminders_text = '\n'.join(lines)
            await message.answer(
                f'Твои напоминания:\n\n{reminders_text}',
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            await message.answer(
                'У тебя нет будущих напоминаний ⚠️',
                reply_markup=ReplyKeyboardRemove(),
            )

    except Exception as e:
        logger.exception('Ошибка при получении напоминаний: %s.', e)
        await message.answer(
            'Ошибка при получении напоминаний 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )

@router.message(StateFilter(None), Command('show_timezone'))
async def show_timezone(message: Message, conn: asyncpg.Connection) -> None:
    try:
        user = await get_user(message.from_user.id, conn)

        if timezone:
            await message.answer(
                f'Твой часовой пояс: {user['timezone']} 🌐',
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            await message.answer(
                f'Часовой пояс не указан ⚠️ Укажи часовой пояс',
                reply_markup=ReplyKeyboardRemove(),
            )

    except Exception as e:
        logger.exception('Ошибка при получении часового пояса: %s.', e)
        await message.answer(
            'Ошибка при получении часового пояса 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )

@router.message(StateFilter(None), Command('help'))
async def show_help(message: Message) -> None:
    await message.answer(
        'Чтобы создать напоминание, отправь сообщение в формате:\n'
        '<дата> <время> <текст напоминания>\n\n'
        'Поддерживаются разные форматы даты и времени, например:\n'
        '- Сегодня 12:00 …\n'
        '- Завтра 12:30 …\n'
        f'- {(date.today() + timedelta(days=3)).strftime("%d.%m.%Y")} 13:00 …\n'
        f'- {(date.today() + timedelta(days=3)).strftime("%d/%m/%Y")} 14:00 …\n'
        f'- {(date.today() + timedelta(days=3)).strftime("%d %B %Y")} 15:00 …\n'
        '- Через 2 часа …\n'
        '- 16:00 … (сегодня или завтра, если время уже прошло)\n\n'
        'Примеры:\n'
        f'{reminder_creation_message_example}',
        reply_markup=ReplyKeyboardRemove(),
    )

@router.message(StateFilter(None))
async def start_create_reminder(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    try:
        error_message = (
            'Неверный формат ⚠️ Используй примеры:\n'
            f'{reminder_creation_message_example}'
        )

        user = await get_user(message.from_user.id, conn)
        user_timezone = user['timezone'] or 'UTC'

        parsed = parse_reminder_input(message.text, user_timezone)
        if parsed is None:
            raise ValueError(error_message)
        remind_at, remind_text = parsed

        remind_at_utc = remind_at.replace(tzinfo=ZoneInfo(user_timezone)).astimezone(timezone.utc)
        now_utc = datetime.now(timezone.utc)

        if remind_at_utc <= now_utc:
            raise ValueError(
                'Время напоминания не может совпадать с настоящим '
                'или быть в прошлом ⚠️ Укажи время в будущем'
            )

        await message.answer(
                    f'Ты хочешь создать это напоминание? ⚠️\n\n'
                    f'📅 {remind_at:%d.%m.%Y %H:%M}\n'
                    f'💬 {remind_text}',
                    reply_markup=keyboards.confirm_create_reminder_kb,
                )

        await state.update_data(reminder={'remind_at_utc': remind_at_utc, 'remind_text': remind_text})
        await state.set_state(MainStates.waiting_for_create_confirmation)

    except ValueError as e:
        await message.answer(
            str(e),
            reply_markup=ReplyKeyboardRemove(),
        )

    except Exception as e:
        logger.exception('Ошибка при создании напоминания: %s.', e)
        await message.answer(
            'Произошла ошибка при создании напоминания 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )

@router.message(MainStates.waiting_for_create_confirmation)
async def confirm_create_reminder(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    try:
        user_choice = message.text.strip()

        if user_choice != commands.get('create'):
            await message.answer(
                'Выбери один из вариантов на клавиатуре ⚠️',
            )
            return

        user = await get_user(message.from_user.id, conn)

        data = await state.get_data()
        reminder = data.get('reminder')

        await add_user_reminder(user['id'], reminder['remind_text'], reminder['remind_at_utc'], conn)

        remind_at = reminder['remind_at_utc'].replace(tzinfo=timezone.utc).astimezone(ZoneInfo(user['timezone'] or 'UTC'))

        await message.answer(
            f'Напоминание создано на {remind_at:%d.%m.%Y %H:%M} ✅',
            reply_markup=ReplyKeyboardRemove(),
        )

        await state.clear()

    except Exception as e:
        logger.exception('Ошибка при подтверждении создания напоминания: %s.', e)
        await message.answer(
            'Ошибка при создании напоминания 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
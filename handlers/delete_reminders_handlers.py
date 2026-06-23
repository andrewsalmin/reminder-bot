import logging
from datetime import timezone
from zoneinfo import ZoneInfo

import asyncpg
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards import keyboards
from utils.db import get_user_reminder, get_user_reminders, get_user, delete_user_reminder, get_nearest_user_reminder
from utils.misc import commands
from .main_handlers import show_reminders

router = Router()
logger = logging.getLogger(__name__)

class DeleteRemindersStates(StatesGroup):
    waiting_for_id = State()
    waiting_for_delete_confirmation = State()

@router.message(StateFilter(None), Command('delete_reminder', 'delete_nearest_reminder', 'delete_all_reminders'))
async def start_delete_reminder(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    try:
        command = message.text.split()[0].lstrip('/')

        if command == 'delete_reminder':
            if await has_reminders(message, conn):
                await show_reminders(message, conn)

                await message.answer(
                    'Введи номер напоминания, которое хочешь удалить 🗑',
                    reply_markup=keyboards.cancel_kb,
                )

                await state.set_state(DeleteRemindersStates.waiting_for_id)
        elif command == 'delete_nearest_reminder':
            if await has_reminders(message, conn):
                await show_reminders(message, conn)

                user = await get_user(message.from_user.id, conn)
                reminder = await get_nearest_user_reminder(user['id'], conn)

                local_time = reminder['remind_at'].replace(tzinfo=timezone.utc).astimezone(ZoneInfo(user['timezone'] or 'UTC'))
                await message.answer(
                    f'Ты хочешь удалить это напоминание? ⚠️\n\n'
                    f'📅 {local_time:%d.%m.%Y %H:%M}\n'
                    f'💬 {reminder['text']}',
                    reply_markup=keyboards.confirm_delete_reminder_kb,
                )

                await state.update_data(reminders_id=[reminder['id']])
                await state.set_state(DeleteRemindersStates.waiting_for_delete_confirmation)
        elif command == 'delete_all_reminders':
            if await has_reminders(message, conn):
                await show_reminders(message, conn)

                user = await get_user(message.from_user.id, conn)
                reminders = await get_user_reminders(user['id'], conn)

                await message.answer(
                    'Ты действительно хочешь удалить все напоминания? ⚠️',
                    reply_markup=keyboards.confirm_delete_reminder_kb,
                )

                await state.update_data(reminders_id=[reminder['id'] for reminder in reminders])
                await state.set_state(DeleteRemindersStates.waiting_for_delete_confirmation)

    except Exception as e:
        logger.exception('Ошибка при подготовке к удалению напоминания(-ий): %s.', e)
        await message.answer(
            'Ошибка при удалении напоминания(-ий) 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )

@router.message(DeleteRemindersStates.waiting_for_id)
async def process_delete_reminder(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    try:
        if not message.text.isdigit():
            await message.answer(
                'Введи ID напоминания ⚠️',
                reply_markup=keyboards.cancel_kb,
            )
            return

        reminder_id = int(message.text)

        user = await get_user(message.from_user.id, conn)

        reminder = await get_user_reminder(reminder_id, user['id'], conn)
        if not reminder:
            await message.answer(
                'Напоминание с таким ID не найдено ⚠️ Введи корректный ID',
                reply_markup=keyboards.cancel_kb,
            )
            return

        local_time = reminder['remind_at'].replace(tzinfo=timezone.utc).astimezone(ZoneInfo(user['timezone'] or 'UTC'))

        await message.answer(
            f'Ты хочешь удалить это напоминание? ⚠️\n\n'
            f'📅 {local_time:%d.%m.%Y %H:%M}\n'
            f'💬 {reminder['text']}',
            reply_markup=keyboards.confirm_delete_reminder_kb,
        )

        await state.update_data(reminders_id=[reminder_id])
        await state.set_state(DeleteRemindersStates.waiting_for_delete_confirmation)

    except Exception as e:
        logger.exception('Ошибка при обработке ID напоминания: %s.', e)
        await message.answer(
            'Ошибка при удалении напоминания(-ий) 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()

@router.message(DeleteRemindersStates.waiting_for_delete_confirmation)
async def confirm_delete_reminder(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    try:
        user_choice = message.text.strip()

        if user_choice != commands.get('delete'):
            await message.answer(
                'Выбери один из вариантов на клавиатуре ⚠️',
            )
            return

        user = await get_user(message.from_user.id, conn)

        data = await state.get_data()
        reminders_id = data.get('reminders_id')

        count = 0
        for reminder_id in reminders_id:
            deleted = await delete_user_reminder(reminder_id, user['id'], conn)
            _, count_str = deleted.split()
            count += int(count_str)

        if count == 0:
            if len(reminders_id) == 1:
                answer = 'Напоминание уже было удалено ⚠️'
            else:
                answer = 'Напоминания уже были удалены ⚠️'
            await message.answer(
                answer,
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            if len(reminders_id) == 1:
                answer = f'Напоминание #{reminders_id[0]} успешно удалено 🗑'
            else:
                answer = f'Напоминания {', '.join([f'#{reminder_id}' for reminder_id in sorted(reminders_id)])} успешно удалены 🗑'
            await message.answer(
                answer,
                reply_markup=ReplyKeyboardRemove(),
            )

        await state.clear()

    except Exception as e:
        logger.exception('Ошибка при подтверждении удаления напоминания(-ий): %s.', e)
        await message.answer(
            'Ошибка при удалении напоминания(-ий) 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()

async def has_reminders(message: Message, conn: asyncpg.Connection) -> bool:
    try:
        user = await get_user(message.from_user.id, conn)

        reminders = await get_user_reminders(user['id'], conn)
        if not reminders:
            await message.answer(
                'У тебя нет будущих напоминаний ⚠️',
                reply_markup=ReplyKeyboardRemove(),
            )
            return False

        return True

    except Exception as e:
        logger.exception('Ошибка при получении напоминаний: %s.', e)
        await message.answer(
            'Ошибка при получении напоминаний 🛑 Попробуй позже',
            reply_markup=ReplyKeyboardRemove(),
        )
        return False
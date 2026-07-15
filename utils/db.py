from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, AsyncIterator

import asyncpg
from aiogram.types import Message

@asynccontextmanager
async def create_db_pool(dsn: str) -> AsyncIterator[asyncpg.Pool]:
    pool = await asyncpg.create_pool(dsn=dsn)
    try:
        yield pool
    finally:
        await pool.close()

async def create_or_update_user(message: Message, conn: asyncpg.Connection) -> None:
    await conn.execute(
        '''
        INSERT INTO users (telegram_id, username)
        VALUES ($1, $2)
        ON CONFLICT (telegram_id) DO UPDATE
            SET username = EXCLUDED.username
        ''',
        message.from_user.id,
        message.from_user.username,
    )

async def get_user(telegram_id: int, conn: asyncpg.Connection) -> Optional[asyncpg.Record]:
    return await conn.fetchrow(
        '''
        SELECT * FROM users
        WHERE telegram_id = $1
        ''',
        telegram_id,
    )

async def get_all_reminders(now_utc: datetime, conn: asyncpg.Connection) -> list[asyncpg.Record]:
    return await conn.fetch(
        '''
        SELECT r.id, u.telegram_id, r.text
        FROM reminders r
        JOIN users u ON r.user_id = u.id
        WHERE r.sent = FALSE AND r.remind_at <= $1
        ORDER BY remind_at, created_at
        ''',
        now_utc,
    )

async def update_reminder_status(reminder_id: int, conn: asyncpg.Connection) -> None:
    await conn.execute(
        '''
        UPDATE reminders
        SET sent = TRUE
        WHERE id = $1
        ''',
        reminder_id,
    )

async def get_user_reminders(user_id: int, conn: asyncpg.Connection) -> list[asyncpg.Record]:
    return await conn.fetch(
        '''
        SELECT * FROM reminders
        WHERE user_id = $1 AND remind_at > NOW() AT TIME ZONE 'UTC'
        ORDER BY remind_at, created_at
        ''',
        user_id,
    )

async def add_user_reminder(user_id: int, remind_text: str, remind_at: datetime, conn: asyncpg.Connection) -> None:
    await conn.execute(
        'INSERT INTO reminders (user_id, text, remind_at) VALUES ($1, $2, $3)',
        user_id,
        remind_text,
        remind_at,
    )

async def get_user_reminder(reminder_id: int, user_id: int, conn: asyncpg.Connection) -> Optional[asyncpg.Record]:
    return await conn.fetchrow(
        '''
        SELECT * FROM reminders
        WHERE id = $1 AND user_id = $2 AND remind_at > NOW() AT TIME ZONE 'UTC'
        ''',
        reminder_id,
        user_id,
    )

async def get_nearest_user_reminder(user_id: int, conn: asyncpg.Connection) -> Optional[asyncpg.Record]:
    return await conn.fetchrow(
        '''
        SELECT * FROM reminders
        WHERE user_id = $1 AND remind_at > NOW() AT TIME ZONE 'UTC'
        ORDER BY remind_at, created_at
        LIMIT 1
        ''',
        user_id,
    )

async def delete_user_reminder(reminder_id: int, user_id: int, conn: asyncpg.Connection) -> str:
    return await conn.execute(
        '''
        DELETE FROM reminders
        WHERE id = $1 AND user_id = $2
        ''',
        reminder_id,
        user_id,
    )

async def update_timezone(telegram_id: int, timezone: str, conn: asyncpg.Connection) -> None:
    await conn.execute(
        '''
        UPDATE users
        SET timezone = $1
        WHERE telegram_id = $2
        ''',
        timezone,
        telegram_id,
    )
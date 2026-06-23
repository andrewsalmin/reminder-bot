import asyncio
from datetime import datetime, timezone
from os import getenv

import asyncpg
from aiogram import Bot
from dotenv import load_dotenv

from utils.db import create_db_pool, get_all_reminders, update_reminder_status
from utils.logger import setup_logger

logger = setup_logger()

async def send_due_reminders(bot: Bot, conn: asyncpg.Connection) -> None:
    try:
        now_utc = datetime.now(timezone.utc)

        rows = await get_all_reminders(now_utc, conn)

        if rows:
            logger.info(f'Найдено {len(rows)} уведомлений к отправке.')

            for row in rows:
                telegram_id = row['telegram_id']

                await bot.send_message(
                    chat_id=telegram_id,
                    text=f'Напоминание 🔔\n{row['text']}'
                )
                await update_reminder_status(row['id'], conn)

                logger.info(f'Уведомление отправлено пользователю {telegram_id}.')
    except Exception as e:
        logger.exception('Ошибка при отправке уведомления: %s.', e)

async def main() -> None:
    load_dotenv()
    token = getenv('BOT_TOKEN')
    db_dsn = getenv('DATABASE_URL')

    if not all([token, db_dsn]):
        logger.error('Отсутствуют необходимые переменные окружения ⚠️')
        return

    bot = Bot(token=token)

    try:
        async with create_db_pool(db_dsn) as pool:
            async with pool.acquire() as conn:
                await send_due_reminders(bot, conn)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
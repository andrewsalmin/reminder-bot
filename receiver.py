import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from handlers import register_handlers
from middlewares.db import DbConnectionMiddleware
from utils.db import create_db_pool
from utils.logger import setup_logger

logger = setup_logger()

async def main() -> None:
    load_dotenv()
    token = getenv('BOT_TOKEN')
    db_dsn = getenv('DATABASE_URL')

    if not all([token, db_dsn]):
        logger.error('Отсутствуют необходимые переменные окружения ⚠️')
        return

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())

    async with create_db_pool(db_dsn) as pool:
        dp.message.middleware(DbConnectionMiddleware(pool))
        register_handlers(dp)
        await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
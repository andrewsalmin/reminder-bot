import logging
from typing import Any, Callable, Dict, Awaitable

import asyncpg
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message

from utils.db import create_or_update_user

logger = logging.getLogger(__name__)

class DbConnectionMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        async with self.pool.acquire() as conn:
            tx = conn.transaction()
            await tx.start()
            try:
                if isinstance(event, Message) and event.from_user:
                    await create_or_update_user(event, conn)

                data['conn'] = conn
                result = await handler(event, data)
                await tx.commit()
                return result
            except asyncpg.PostgresError as err:
                logger.exception('Ошибка БД: %s.', err)

                try:
                    await tx.rollback()
                except Exception as e:
                    logger.exception('Ошибка отката транзакции после ошибки БД: %s.', e)
                try:
                    if isinstance(event, Message):
                        await event.reply('Произошла ошибка базы данных 🛑 Попробуй позже')
                except Exception as e:
                    logger.exception('Ошибка отправки сообщения пользователю после ошибки БД: %s.', e)

                return None
            except Exception as exc:
                logger.exception('Непредвиденная ошибка: %s.', exc)

                try:
                    await tx.rollback()
                except Exception as e:
                    logger.exception('Ошибка отката транзакции после непредвиденной ошибки: %s.', e)
                try:
                    if isinstance(event, Message):
                        await event.reply('Произошла внутренняя ошибка 🛑 Попробуй позже.')
                except Exception as e:
                    logger.exception('Ошибка отправки сообщения пользователю после непредвиденной ошибки: %s.', e)

                return None
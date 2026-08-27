# Filename: app/bot/middlewares.py
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)

class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware to inject an async database session into every handler.
    Ensures safe creation and teardown of DB connections per Telegram update.
    """
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_pool() as session:
            # Inject session into data dict so handlers can access it
            data["db_session"] = session
            try:
                return await handler(event, data)
            except Exception as e:
                logger.error(f"Error in handler with DB session: {e}")
                # Rollback in case of an error during a transaction
                await session.rollback()
                raise
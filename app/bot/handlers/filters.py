# Filename: app/bot/handlers/filters.py
import logging
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Filter

logger = logging.getLogger(__name__)
filters_router = Router()

# Note: This router should be added LAST in the dispatcher so it doesn't intercept commands
@filters_router.message(F.text & (F.chat.type.in_({"group", "supergroup"})))
async def check_filters(message: Message, db_session: AsyncSession):
    """
    Checks incoming text messages against the database filters for the specific group.
    """
    chat_id = message.chat.id
    text = message.text.lower()

    # Query filters for this group
    stmt = select(Filter).where(Filter.group_id == chat_id)
    result = await db_session.execute(stmt)
    group_filters = result.scalars().all()

    for custom_filter in group_filters:
        # Exact match or word boundary matching can be implemented here
        if custom_filter.keyword.lower() in text:
            await message.reply(custom_filter.reply_text)
            break # Stop after finding the first matching filter
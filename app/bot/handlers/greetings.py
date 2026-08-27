# Filename: app/bot/handlers/greetings.py
import logging
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Group
from app.config import settings

logger = logging.getLogger(__name__)
greetings_router = Router()

@greetings_router.message(F.new_chat_members)
async def on_new_chat_members(message: Message, db_session: AsyncSession):
    """
    Handles new members joining the group.
    - Strict Anti-Bot Logic: If a bot is added by a non-admin, kick the bot.
    - Welcome Message: Pulls custom welcome message from the database.
    """
    adder_id = message.from_user.id
    chat_id = message.chat.id

    # Check if the adder is an admin/owner
    is_adder_admin = False
    if adder_id == settings.owner_id:
        is_adder_admin = True
    else:
        try:
            member = await message.bot.get_chat_member(chat_id, adder_id)
            is_adder_admin = member.status in ("administrator", "creator")
        except Exception:
            pass

    for new_member in message.new_chat_members:
        # STRICT ANTI-BOT SYSTEM
        if new_member.is_bot and new_member.id != message.bot.id:
            if not is_adder_admin:
                # Unauthorized bot addition detected
                try:
                    await message.chat.ban(user_id=new_member.id)
                    await message.chat.unban(user_id=new_member.id) # Kick bot
                    await message.reply(f"🚨 သတိပေးချက်: Admin မဟုတ်သူများ Bot အသစ်ထည့်ခွင့်မပြုပါ။ @{new_member.username} ကို Kick လိုက်ပါပြီ။")
                    continue
                except Exception as e:
                    logger.error(f"Failed to kick unauthorized bot: {e}")
            else:
                # Admin added the bot, allow it
                pass 
        
        # WELCOME MESSAGE LOGIC (For normal users)
        if not new_member.is_bot:
            stmt = select(Group).where(Group.id == chat_id)
            result = await db_session.execute(stmt)
            group_data = result.scalar_one_or_none()

            welcome_text = f"👋 မင်္ဂလာပါ {new_member.full_name}၊ Group မှ ကြိုဆိုပါတယ်။"
            
            if group_data and group_data.welcome_message:
                # Simple placeholder replacement
                welcome_text = group_data.welcome_message.replace("{name}", new_member.full_name)
            
            await message.answer(welcome_text)
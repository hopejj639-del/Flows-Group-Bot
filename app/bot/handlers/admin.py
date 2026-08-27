# Filename: app/bot/handlers/admin.py
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.security import IsGroupAdminFilter
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
admin_router = Router()
# Apply Admin filter to all handlers in this router
admin_router.message.filter(IsGroupAdminFilter())

@admin_router.message(Command("ban"))
async def ban_user(message: Message):
    if not message.reply_to_message:
        return await message.reply("Ban လုပ်ရန်အတွက် user ၏ စာကို Reply ပြန်ပြီး /ban ဟု ရိုက်ပါ။")
    
    target_user = message.reply_to_message.from_user
    if target_user.id == message.bot.id:
        return await message.reply("Bot ကိုယ်တိုင်ကို Ban လို့ မရပါ။")

    try:
        await message.chat.ban(user_id=target_user.id)
        await message.reply(f"🚨 {target_user.full_name} ကို Group မှ Ban လိုက်ပါပြီ။")
    except Exception as e:
        logger.error(f"Ban failed: {e}")
        await message.reply("Ban လုပ်ရန် Bot တွင် Admin အခွင့်အရေး မရှိပါ (သို့) Error ဖြစ်နေပါသည်။")

@admin_router.message(Command("kick"))
async def kick_user(message: Message):
    if not message.reply_to_message:
        return await message.reply("Kick လုပ်ရန်အတွက် user ၏ စာကို Reply ပြန်ပြီး /kick ဟု ရိုက်ပါ။")
    
    target_user = message.reply_to_message.from_user
    try:
        # Unban immediately after ban acts as a "Kick" in Telegram
        await message.chat.ban(user_id=target_user.id)
        await message.chat.unban(user_id=target_user.id)
        await message.reply(f"👢 {target_user.full_name} ကို Group မှ Kick ထုတ်လိုက်ပါပြီ။")
    except Exception as e:
        logger.error(f"Kick failed: {e}")
        await message.reply("Kick လုပ်ရန် Bot တွင် အခွင့်အရေး မရှိပါ။")

@admin_router.message(Command("purge"))
async def purge_messages(message: Message):
    """
    Deletes messages from the replied message down to the command message.
    Note: Telegram API has limits on bulk deletion, this is a basic loop implementation.
    """
    if not message.reply_to_message:
        return await message.reply("ဖျက်လိုသော အစစာတန်းကို Reply ပြန်ပြီး /purge ဟုရိုက်ပါ။")
    
    start_id = message.reply_to_message.message_id
    end_id = message.message_id
    deleted_count = 0

    # Telegram allows deleting max 100 messages at once, but for simplicity we loop here
    # A production-grade purge would use delete_messages (plural) API.
    message_ids_to_delete = list(range(start_id, end_id + 1))
    
    try:
        # Using aiogram 3.x bulk delete
        await message.bot.delete_messages(chat_id=message.chat.id, message_ids=message_ids_to_delete)
        deleted_count = len(message_ids_to_delete)
    except Exception as e:
        logger.error(f"Purge failed: {e}")
        return await message.reply("စာများဖျက်ရာတွင် အခက်အခဲရှိနေပါသည် (၁၄ ရက်ထက်ကျော်လွန်သော စာများကို ဖျက်မရပါ)။")

    prompt = await message.answer(f"✅ စာကြောင်းရေ {deleted_count} ကြောင်းကို ရှင်းလင်းလိုက်ပါပြီ။")
    
    # Optional: Delete the success prompt after a few seconds using asyncio/background task.
# Filename: app/bot/handlers/moderation.py
import logging
import re
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)
moderation_router = Router()

async def check_admin(message: Message) -> bool:
    """
    Helper function to check if the user issuing the command is an Admin or Owner.
    Implements Option A (Telegram Native Admin Check).
    """
    if message.chat.type == "private":
        return False
        
    try:
        member = await message.chat.get_member(message.from_user.id)
        return member.status in ("creator", "administrator")
    except Exception as e:
        logger.error(f"Failed to check admin status for user {message.from_user.id}: {e}")
        return False

def parse_duration(duration_str: str) -> int | None:
    """
    Parses time suffix strings like '30m', '12h', '3d' into total seconds.
    Returns None if the format is invalid.
    """
    match = re.match(r"^(\d+)([mhd])$", duration_str.lower())
    if not match:
        return None
        
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
        
    return None

@moderation_router.message(Command("mute"))
async def cmd_mute(message: Message):
    if message.chat.type == "private":
        await message.reply("⚠️ ဤ Command ကို Group ထဲတွင်သာ အသုံးပြုနိုင်ပါသည်။")
        return

    if not await check_admin(message):
        await message.reply("❌ ဤ Command ကို အသုံးပြုရန် Admin ဖြစ်ရန် လိုအပ်ပါသည်။")
        return

    if not message.reply_to_message:
        await message.reply("⚠️ Mute လုပ်လိုသူ၏ စာကို Reply ပြန်၍ /mute <အချိန်> ဟု ရိုက်ပါ။\n(ဥပမာ - /mute 1h သို့မဟုတ် /mute 3d)")
        return

    target_user = message.reply_to_message.from_user
    if not target_user:
        return

    me = await message.bot.me()
    if target_user.id == me.id or target_user.id == message.from_user.id:
        await message.reply("⚠️ ဤသူ့ကို Mute လုပ်၍ မရပါ။")
        return

    args = message.text.split()
    duration_seconds = 86400  # Default: 1 Day
    duration_text = "၁ ရက်"

    if len(args) > 1:
        parsed_sec = parse_duration(args[1])
        if parsed_sec is None:
            await message.reply("❌ ပုံစံ မှားယွင်းနေပါသည်။ (ဥပမာ: `/mute 30m`, `/mute 12h`, `/mute 3d` ဟု သုံးပါ)")
            return
        duration_seconds = parsed_sec
        duration_text = args[1]

    until_date = datetime.now() + timedelta(seconds=duration_seconds)
    
    # Mute လုပ်ရာတွင် အားလုံးကို ပိတ်မည်
    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False
    )

    try:
        await message.chat.restrict(
            user_id=target_user.id,
            permissions=permissions,
            until_date=until_date
        )
        await message.reply(f"🔇 <b>{target_user.full_name}</b> အား <b>{duration_text}</b> ကြာ Mute လိုက်ပါပြီ။")
    except TelegramBadRequest as e:
        logger.error(f"Failed to mute user {target_user.id}: {e}")
        await message.reply("❌ Bot တွင် Member များကို Restrict လုပ်ရန် Admin Right (Ban Users) မရှိပါ။")

@moderation_router.message(Command("unmute"))
async def cmd_unmute(message: Message):
    """
    Unmutes a restricted user, restoring full chat permissions including stickers and media.
    Must be used by replying to the target user's message.
    """
    if message.chat.type == "private":
        await message.reply("⚠️ ဤ Command ကို Group ထဲတွင်သာ အသုံးပြုနိုင်ပါသည်။")
        return

    if not await check_admin(message):
        await message.reply("❌ ဤ Command ကို အသုံးပြုရန် Admin ဖြစ်ရန် လိုအပ်ပါသည်။")
        return

    if not message.reply_to_message:
        await message.reply("⚠️ Unmute လုပ်လိုသူ၏ စာကို Reply ပြန်၍ /unmute ဟု ရိုက်ပါ။")
        return

    target_user = message.reply_to_message.from_user
    if not target_user:
        return

    # ARCHITECTURAL FIX: 
    # Enable all required permissions including `can_send_other_messages=True` 
    # to fix the sticker restriction issue.
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,      # လိုအပ်သော Sticker, GIF များ ပို့ခွင့် ဖွင့်ပေးခြင်း
        can_add_web_page_previews=True,
        can_invite_users=True
    )

    try:
        await message.chat.restrict(
            user_id=target_user.id,
            permissions=permissions
        )
        await message.reply(f"🔊 <b>{target_user.full_name}</b> ၏ Mute အမိန့်ကို ရုပ်သိမ်းလိုက်ပါပြီ။ ယခုအခါ စာ၊ ဓာတ်ပုံနှင့် Sticker များ ပို့နိုင်ပါပြီ။")
    except TelegramBadRequest as e:
        logger.error(f"Failed to unmute user {target_user.id}: {e}")
        await message.reply("❌ Bot တွင် လုံလောက်သော Admin Right မရှိပါ။")

# Filename: app/bot/handlers/general.py
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
general_router = Router()

@general_router.message(CommandStart())
async def cmd_start(message: Message, db_session: AsyncSession, **kwargs):
    welcome_text = (
        f"👋 မင်္ဂလာပါ {message.from_user.full_name}!\n\n"
        "ကျွန်တော်ကတော့ Flows Group များကို စီမံခန့်ခွဲပေးမည့် Bot ဖြစ်ပါတယ်။\n"
        "Bot ကို အသုံးပြုရန် သင့် Group ထဲသို့ Add ပြီး Admin Privilege အပြည့်အဝ ပေးထားရန် လိုအပ်ပါသည်။"
    )
    await message.reply(welcome_text)

@general_router.message(Command("help"))
async def cmd_help(message: Message, db_session: AsyncSession, **kwargs):
    help_text = "🛠 **Admin Commands (Owner သာ သုံးခွင့်ရှိသည်):**\n..."
    await message.reply(help_text)

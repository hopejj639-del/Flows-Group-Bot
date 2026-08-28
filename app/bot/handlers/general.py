# Filename: app/bot/handlers/general.py
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

logger = logging.getLogger(__name__)
general_router = Router()

@general_router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handles the /start command in private chats or groups.
    """
    welcome_text = (
        f"👋 မင်္ဂလာပါ {message.from_user.full_name}!\n\n"
        "ကျွန်တော်ကတော့ Flows Group များကို စီမံခန့်ခွဲပေးမည့် Bot ဖြစ်ပါတယ်။\n"
        "Bot ကို အသုံးပြုရန် သင့် Group ထဲသို့ Add ပြီး Admin Privilege အပြည့်အဝ ပေးထားရန် လိုအပ်ပါသည်။\n\n"
        "အကူအညီလိုပါက /help ဟု ရိုက်နှိပ်နိုင်ပါသည်။"
    )
    await message.reply(welcome_text)

@general_router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Handles the /help command.
    """
    help_text = (
        "🛠 **Admin Commands (Owner သာ သုံးခွင့်ရှိသည်):**\n"
        "/ban (စာကို Reply ပြန်၍)\n"
        "/kick (စာကို Reply ပြန်၍)\n"
        "/purge (ဖျက်လိုသော အစစာတန်းကို Reply ပြန်၍)\n\n"
        "Group အတွင်း Bot အသစ်များ ဝင်လာပါက အလိုအလျောက် Kick ထုတ်ပေးမည့် စနစ်ပါဝင်ပါသည်။"
    )
    await message.reply(help_text)

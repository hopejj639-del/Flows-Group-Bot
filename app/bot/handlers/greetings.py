# Filename: app/bot/handlers/greetings.py
import logging
import html
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)
greetings_router = Router()

# In-Memory State: Group တစ်ခုချင်းစီ၏ နောက်ဆုံး Welcome Message ID များကို မှတ်သားရန်
# Structure: {chat_id: message_id}
last_welcome_messages: dict[int, int] = {}

@greetings_router.message(F.new_chat_members)
async def on_user_joined(message: Message):
    """
    Handles new members joining the group.
    Features: Anti-bot security, System message cleanup, Auto-delete previous welcome, and Inline buttons.
    """
    chat_id = message.chat.id
    
    # ၁။ System Message ရှင်းလင်းရေး ("User joined the group" စာတန်းကို အလိုအလျောက် ဖျက်မည်)
    try:
        await message.delete()
    except TelegramBadRequest:
        logger.warning(f"Failed to delete system joined message in chat {chat_id}. Missing 'Delete Messages' admin right?")
        pass # Admin Permission မရှိပါက Error မတက်စေရန် ကျော်သွားပါမည်

    new_members = message.new_chat_members
    if not new_members:
        return

    for member in new_members:
        # ၂။ Anti-Bot Security (Bot အသစ်များ ဝင်လာပါက ချက်ချင်း Kick ထုတ်မည်)
        if member.is_bot:
            # မိမိကိုယ်တိုင် (Flows Group Bot) Group ထဲ Add ခံရချိန်တွင် Kick မထုတ်မိစေရန် စစ်ဆေးခြင်း
            me = await message.bot.me()
            if member.id == me.id:
                continue
                
            try:
                # Bot ကို Ban ပြီး ချက်ချင်းပြန် Unban လုပ်ခြင်းသည် Kick ထုတ်ခြင်း (Remove from group) နှင့် အတူတူပင်ဖြစ်သည်
                await message.chat.ban(user_id=member.id)
                await message.chat.unban(user_id=member.id)
                logger.info(f"Anti-Bot Triggered: Kicked unauthorized bot {member.full_name} ({member.id}) from chat {chat_id}")
            except TelegramBadRequest as e:
                logger.error(f"Failed to kick bot {member.id} in chat {chat_id}. Missing 'Ban Users' right? Error: {e}")
            continue # Bot ဖြစ်နေပါက Welcome Message ပို့မည့် အဆင့်သို့ ဆက်မသွားဘဲ ကျော်မည်

        # ၃။ Auto-Delete System (အရင်ကြိုဆိုထားသော စာဟောင်း ရှိပါက ဖျက်မည်)
        if chat_id in last_welcome_messages:
            prev_msg_id = last_welcome_messages[chat_id]
            try:
                await message.bot.delete_message(chat_id=chat_id, message_id=prev_msg_id)
            except TelegramBadRequest:
                # အကယ်၍ Admin တစ်ယောက်ယောက်က Manual ဖျက်သွားပြီးဖြစ်ပါက Error ကို လျစ်လျူရှုမည်
                pass

        # ၄။ Interactive UI (Inline Keyboard Buttons တည်ဆောက်ခြင်း)
        # မှတ်ချက်: "URL" နေရာတွင် သင်၏ အမှန်တကယ် Link များကို ပြင်ဆင်ထည့်သွင်းပါ
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📜 စည်းကမ်းချက်များ ဖတ်ရန်", url="https://t.me/your_rules_link"),
                    InlineKeyboardButton(text="📢 Channel သို့ ဝင်ရန်", url="https://t.me/your_channel_link")
                ]
            ]
        )

        # HTML Injection မှ ကာကွယ်ရန် html.escape ကို အသုံးပြုထားပါသည်
        safe_name = html.escape(member.full_name)
        safe_chat_title = html.escape(message.chat.title)

        welcome_text = (
            f"👋 မင်္ဂလာပါ <a href='tg://user?id={member.id}'>{safe_name}</a>!\n\n"
            f"<b>{safe_chat_title}</b> မှ နွေးထွေးစွာ ကြိုဆိုပါတယ်။\n"
            "Group အတွင်း စည်းကမ်းချက်များကို လိုက်နာပေးရန် မေတ္တာရပ်ခံအပ်ပါသည်။"
        )

        # ၅။ ကြိုဆိုစာသား အသစ်ပို့ခြင်း နှင့် In-Memory တွင် မှတ်သားခြင်း
        try:
            sent_msg = await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")
            # နောက်လူဝင်လာပါက ဖျက်နိုင်ရန် ယခု Message ID ကို မှတ်သားထားမည်
            last_welcome_messages[chat_id] = sent_msg.message_id
        except Exception as e:
            logger.error(f"Failed to send welcome message in chat {chat_id}: {e}")

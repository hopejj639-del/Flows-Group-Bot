# Filename: app/security.py
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from app.config import settings

class IsOwnerFilter(BaseFilter):
    """
    Strict Authorization Layer.
    Only allows the owner (defined in .env OWNER_ID) to execute the command.
    Prevents unauthorized individuals from controlling your bot.
    """
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        user_id = obj.from_user.id
        return user_id == settings.owner_id

class IsGroupAdminFilter(BaseFilter):
    """
    Checks if the user triggering the command is an admin in the group.
    The single bot owner inherently bypasses this check (Super Admin privilege).
    """
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        
        # Bot owner always has privileges
        if user_id == settings.owner_id:
            return True
            
        chat_id = message.chat.id
        # In a private chat, there are no admins, so return False
        if message.chat.type == "private":
            return False

        try:
            member = await message.bot.get_chat_member(chat_id, user_id)
            return member.status in ("administrator", "creator")
        except Exception:
            # Fail securely if API call fails or bot lacks privileges
            return False
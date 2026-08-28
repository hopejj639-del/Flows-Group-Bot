# Filename: app/bot/dispatcher.py
from aiogram import Dispatcher
from app.database import AsyncSessionLocal
from app.bot.middlewares import DatabaseMiddleware
from app.bot.handlers.general import general_router
# Import other routers here...

def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    
    # Bind Middleware
    dp.update.middleware(DatabaseMiddleware(session_pool=AsyncSessionLocal))

    # Bind Routers
    dp.include_router(general_router)
    # dp.include_router(admin_router)
    # dp.include_router(greetings_router)

    return dp

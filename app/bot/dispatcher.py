# Filename: app/bot/dispatcher.py
from aiogram import Dispatcher
from app.database import AsyncSessionLocal
from app.bot.middlewares import DatabaseMiddleware
from app.bot.handlers.general import general_router
from app.bot.handlers.admin import admin_router
from app.bot.handlers.greetings import greetings_router
from app.bot.handlers.filters import filters_router

def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    
    # Bind Middleware (Database injection)
    dp.update.middleware(DatabaseMiddleware(session_pool=AsyncSessionLocal))

    # Bind Routers (Order matters! General commands first, then admin, then greetings, then filters)
    dp.include_router(general_router)
    dp.include_router(admin_router)
    dp.include_router(greetings_router)
    dp.include_router(filters_router)

    return dp

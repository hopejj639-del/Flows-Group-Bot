# Filename: app/bot/dispatcher.py
from aiogram import Dispatcher
from app.database import AsyncSessionLocal
from app.bot.middlewares import DatabaseMiddleware
from app.bot.handlers.admin import admin_router
from app.bot.handlers.greetings import greetings_router
from app.bot.handlers.filters import filters_router

def setup_dispatcher() -> Dispatcher:
    """
    Configures and returns the main aiogram Dispatcher.
    Registers middlewares and routers in the correct order.
    """
    dp = Dispatcher()
    
    # Register Middlewares
    dp.update.middleware(DatabaseMiddleware(session_pool=AsyncSessionLocal))

    # Register Routers (Order matters! Filters should generally be last)
    dp.include_router(admin_router)
    dp.include_router(greetings_router)
    dp.include_router(filters_router)

    return dp
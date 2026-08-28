# Filename: app/bot/dispatcher.py
from aiogram import Dispatcher
from app.database import AsyncSessionLocal
from app.bot.middlewares import DatabaseMiddleware
from app.bot.handlers.admin import admin_router
from app.bot.handlers.greetings import greetings_router
from app.bot.handlers.filters import filters_router
from app.bot.handlers.general import general_router # အသစ်ထည့်ရမည့် Import

def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    
    # Register Middlewares
    dp.update.middleware(DatabaseMiddleware(session_pool=AsyncSessionLocal))

    # Register Routers (Order matters! General commands first, then admin, then filters last)
    dp.include_router(general_router) # အသစ်ထည့်ရမည့် Router
    dp.include_router(admin_router)
    dp.include_router(greetings_router)
    dp.include_router(filters_router)

    return dp

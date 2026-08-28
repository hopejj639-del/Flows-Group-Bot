# Filename: app/api/server.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from app.config import settings
from app.database import init_db
from app.bot.dispatcher import setup_dispatcher

logger = logging.getLogger(__name__)

# Initialize Bot instance with the token from .env
bot = Bot(token=settings.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML"))
dp = setup_dispatcher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan events for startup and shutdown sequences.
    """
    # --- STARTUP ---
    logger.info("Starting up application...")
    # 1. Initialize Database Tables
    await init_db()
    
    # 2. Set Telegram Webhook Securely
    webhook_endpoint = f"{str(settings.webhook_url).rstrip('/')}/webhook"
    webhook_info = await bot.get_webhook_info()
    
    if webhook_info.url != webhook_endpoint:
        # drop_pending_updates=True will clear out the 'pending_update_count: 2'
        await bot.set_webhook(
            url=webhook_endpoint,
            drop_pending_updates=True,
            allowed_updates=dp.resolve_used_update_types()
        )
        logger.info(f"Webhook explicitly set to {webhook_endpoint}")
    else:
        logger.info("Webhook is already configured correctly.")
        
    yield
    
    # --- SHUTDOWN ---
    logger.info("Shutting down application...")
    # CRITICAL ARCHITECTURAL FIX: 
    # Removed `await bot.delete_webhook()` to prevent Render's sleep mode from breaking the bot.
    # The webhook MUST persist so Telegram can wake up the server when a new message arrives.
    await bot.session.close()
    logger.info("Application shutdown gracefully.")

# Initialize FastAPI application
app = FastAPI(lifespan=lifespan, title="Flows Group Bot")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    The endpoint that Telegram hits with new messages/events.
    """
    try:
        # Parse incoming JSON payload into an aiogram Update object
        payload = await request.json()
        update = Update.model_validate(payload, context={"bot": bot})
        
        # Feed the update to our dispatcher (Bot Logic)
        await dp.feed_update(bot=bot, update=update)
        
        # Always return 200 OK immediately so Telegram doesn't retry
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}")
        # Return 200 even on error to prevent Telegram from spamming retries
        return {"ok": False, "error": str(e)}

@app.get("/health")
async def health_check():
    """
    Endpoint for ping services (e.g., UptimeRobot) to keep the Web Service alive.
    """
    return {"status": "alive", "service": "telegram_bot"}

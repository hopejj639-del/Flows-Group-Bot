# Filename: app/config.py
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, HttpUrl

# Logging Configuration for Production-grade observability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class Settings(BaseSettings):
    """
    Application settings mapped from environment variables.
    Utilizes Pydantic for strict type validation.
    """
    bot_token: SecretStr
    database_url: str
    webhook_url: HttpUrl
    owner_id: int # Telegram User ID of the single owner

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instantiating settings to be imported across the app
settings = Settings()
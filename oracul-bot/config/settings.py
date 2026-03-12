"""
Конфигурация приложения Oracul Bot
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    # App
    DEBUG: bool = False

    # Telegram
    BOT_TOKEN: str
    TG_API_ID: str = ""
    TG_API_HASH: str = ""

    # OpenRouter LLM
    OPENROUTER_API_KEY: str = ""
    DEFAULT_MODEL: str = "openai/gpt-oss-120b:free"
    BACKUP_MODEL: str = "openai/gpt-oss-20b:free"
    THIRD_MODEL: str = "nvidia/nemotron-3-nano-30b-a3b:free"
    FOURTH_MODEL: str = "arcee-ai/trinity-mini:free"

    # Groq API для расшифровки голоса
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_WHISPER_MODEL: str = "whisper-large-v3"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./tg_analysis.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Business Logic
    FREE_ANALYSES_PER_MONTH: int = 30

    # AI Settings
    MAX_TEXT_LENGTH: int = 4000
    ANALYSIS_TIMEOUT: int = 30

    class Config:
        # .env находится в корне проекта, на уровень выше oracul-bot/
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        case_sensitive = True
        # Разрешаем дополнительные поля из .env
        extra = "allow"


def get_settings() -> Settings:
    """Получение настроек с обработкой ошибок"""
    try:
        return Settings()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка загрузки настроек: {e}")
        return None


# Глобальный экземпляр (может быть None если .env не настроен)
settings = get_settings()

"""
Главный файл запуска Oracul Bot
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ConversationHandler, filters
)
from fastapi import FastAPI
import uvicorn

from config.settings import settings, validate_settings
from database.connection import init_database, close_database
from bot.handlers import BotHandlers, WAITING_FOR_TEXT, WAITING_FOR_VOICE
from services.analysis_service import AnalysisService
from services.channel_service import ChannelService

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO if not settings.DEBUG else logging.DEBUG
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting Oracul Bot...")
    
    # Валидация настроек
    validate_settings()
    
    # Инициализация БД
    await init_database()
    
    # Запуск Telegram бота
    telegram_app = await setup_telegram_bot()
    await telegram_app.initialize()
    await telegram_app.start()
    
    # Настройка webhook или polling
    if settings.TELEGRAM_WEBHOOK_URL:
        await telegram_app.bot.set_webhook(
            url=f"{settings.TELEGRAM_WEBHOOK_URL}/webhook",
            allowed_updates=Update.ALL_TYPES
        )
        logger.info(f"Webhook set to: {settings.TELEGRAM_WEBHOOK_URL}/webhook")
    else:
        # Запускаем polling в фоне
        asyncio.create_task(telegram_app.updater.start_polling())
        logger.info("Started polling mode")
    
    app.state.telegram_app = telegram_app
    
    yield
    
    # Shutdown
    logger.info("Shutting down Oracul Bot...")
    
    if hasattr(app.state, 'telegram_app'):
        await app.state.telegram_app.stop()
        await app.state.telegram_app.shutdown()
    
    await close_database()


async def setup_telegram_bot():
    """Настройка Telegram бота"""
    # Создаем приложение
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Создаем сервисы
    analysis_service = AnalysisService()
    channel_service = ChannelService()
    handlers = BotHandlers(analysis_service, channel_service)
    
    # Инициализируем сервис каналов
    await channel_service.initialize()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("stats", handlers.stats_command))
    
    # Conversation handler для анализа
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.button_callback)],
        states={
            WAITING_FOR_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.analyze_text_message)
            ],
            WAITING_FOR_VOICE: [
                MessageHandler(filters.VOICE, handlers.analyze_voice_message)
            ],
            WAITING_FOR_CHANNEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.analyze_channel_message)
            ],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_conversation)],
        per_message=False
    )
    
    application.add_handler(conv_handler)
    
    # Обработчик кнопок (вне conversation)
    application.add_handler(CallbackQueryHandler(handlers.button_callback))
    
    # Обработчик текстовых сообщений (прямой анализ)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.analyze_text_message)
    )
    
    # Обработчик голосовых сообщений (прямой анализ)
    application.add_handler(
        MessageHandler(filters.VOICE, handlers.analyze_voice_message)
    )
    
    return application


# FastAPI приложение
app = FastAPI(
    title="Oracul Bot API",
    description="API для мультимодального бота самоанализа",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Oracul Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "timestamp": "2024-12-26T23:00:00Z"
    }


@app.post("/webhook")
async def telegram_webhook(update: dict):
    """Webhook для Telegram"""
    try:
        telegram_app = app.state.telegram_app
        await telegram_app.process_update(Update.de_json(update, telegram_app.bot))
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/stats")
async def get_stats():
    """Получить статистику бота"""
    # TODO: Реализовать получение статистики из БД
    return {
        "total_users": 0,
        "total_analyses": 0,
        "active_users_today": 0
    }


if __name__ == "__main__":
    # Запуск в режиме разработки
    if settings.DEBUG:
        uvicorn.run(
            "main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
            log_level="debug"
        )
    else:
        uvicorn.run(
            "main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info"
        )
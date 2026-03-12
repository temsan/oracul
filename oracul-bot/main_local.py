"""
Главный файл запуска Oracul Bot с локальными моделями
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
from bot.local_handlers import LocalBotHandlers, WAITING_FOR_TEXT, WAITING_FOR_VOICE
from services.local_analysis_service import LocalAnalysisService
from services.channel_service import ChannelService
from services.vllm_service import vllm_service

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
    logger.info("🔮 Starting Oracul Bot with Local Models...")
    
    # Валидация настроек
    validate_settings()
    
    # Инициализация БД
    await init_database()
    
    # Проверяем доступность vLLM
    vllm_available = await vllm_service.health_check()
    if vllm_available:
        logger.info("⚡ vLLM server is available")
        models = await vllm_service.get_models()
        logger.info(f"📋 Available models: {len(models)}")
    else:
        logger.warning("⚠️ vLLM server is not available - some features will be limited")
    
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
    """Настройка Telegram бота с локальными сервисами"""
    # Создаем приложение
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Создаем сервисы
    local_analysis_service = LocalAnalysisService()
    channel_service = ChannelService()
    handlers = LocalBotHandlers(local_analysis_service, channel_service)
    
    # Инициализируем сервис каналов
    await channel_service.initialize()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CommandHandler("models", show_models_info))
    application.add_handler(CommandHandler("vllm", show_vllm_info))
    
    # Conversation handler для анализа
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.button_callback)],
        states={
            WAITING_FOR_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.analyze_text_local)
            ],
            WAITING_FOR_VOICE: [
                MessageHandler(filters.VOICE, handlers.analyze_voice_local)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
        per_message=False
    )
    
    application.add_handler(conv_handler)
    
    # Обработчик кнопок (вне conversation)
    application.add_handler(CallbackQueryHandler(handlers.button_callback))
    
    # Обработчик текстовых сообщений (прямой анализ)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.analyze_text_local)
    )
    
    # Обработчик голосовых сообщений (прямой анализ)
    application.add_handler(
        MessageHandler(filters.VOICE, handlers.analyze_voice_local)
    )
    
    return application


async def show_help(update: Update, context):
    """Показать справку по локальным моделям"""
    help_text = """
🔮 *Oracul Bot - Локальные модели*

*Команды:*
/start - Главное меню
/help - Эта справка
/models - Информация о моделях
/vllm - Статус vLLM сервера

*Локальные возможности:*

🧠 *Анализ текста:*
• RuBERT - тональность на русском языке
• DistilRoBERTa - определение эмоций
• DeepPavlov - эмбеддинги для личности
• vLLM - генеративный анализ

🎤 *Анализ голоса:*
• Whisper - транскрипция речи
• librosa - аудио характеристики
• Локальные модели эмоций

*Преимущества:*
🔒 Полная приватность - данные не покидают сервер
⚡ Высокая скорость - нет задержек API
🌐 Автономность - работа без интернета
💰 Экономия - нет платы за API вызовы

*Системные требования:*
• Python 3.11+
• CUDA (рекомендуется)
• 8GB+ RAM
• 10GB+ свободного места

Техподдержка: @oracul_support
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def show_models_info(update: Update, context):
    """Показать информацию о загруженных моделях"""
    models_text = """
🧠 *Информация о локальных моделях*

*Текстовый анализ:*
• `blanchefort/rubert-base-cased-sentiment` - Тональность
• `j-hartmann/emotion-english-distilroberta-base` - Эмоции
• `DeepPavlov/rubert-base-cased-sentence` - Эмбеддинги
• `ai-forever/rugpt3small_based_on_gpt2` - Генерация

*Голосовой анализ:*
• `whisper-base` - Транскрипция речи
• `librosa` - Аудио обработка

*Статус загрузки:*
Модели загружаются при первом использовании.
Время загрузки: 1-5 минут в зависимости от модели.

*Использование GPU:*
CUDA доступна: Да/Нет (автоопределение)
Ускорение: До 10x быстрее на GPU

*Память:*
Требуется: ~4-8GB RAM
Рекомендуется: 16GB+ для всех моделей
    """
    
    await update.message.reply_text(models_text, parse_mode='Markdown')


async def show_vllm_info(update: Update, context):
    """Показать информацию о vLLM сервере"""
    try:
        is_healthy = await vllm_service.health_check()
        
        if is_healthy:
            models = await vllm_service.get_models()
            
            vllm_text = f"""
⚡ *vLLM Сервер - Активен*

*Статус:* 🟢 Работает
*Доступные модели:* {len(models)}
*Endpoint:* http://localhost:8000

*Загруженные модели:*
"""
            
            for model in models[:10]:  # Показываем первые 10
                vllm_text += f"• {model}\n"
            
            if len(models) > 10:
                vllm_text += f"• ... и еще {len(models) - 10} моделей\n"
            
            vllm_text += """
*Возможности:*
• Высокопроизводительный inference
• Батчинг запросов
• GPU оптимизация
• OpenAI-совместимый API

*Использование:*
Отправь текст для анализа с генеративной моделью!
            """
        else:
            vllm_text = """
⚡ *vLLM Сервер - Недоступен*

*Статус:* 🔴 Не запущен

*Для запуска:*
```bash
pip install vllm
python -m vllm.entrypoints.api_server \\
    --model microsoft/DialoGPT-medium \\
    --host 0.0.0.0 \\
    --port 8000
```

*Альтернативные модели:*
• `microsoft/DialoGPT-medium`
• `ai-forever/rugpt3small_based_on_gpt2`
• `sberbank-ai/rugpt3large_based_on_gpt2`

Без vLLM доступны базовые функции анализа.
            """
        
        await update.message.reply_text(vllm_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error showing vLLM info: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении информации о vLLM сервере"
        )


async def cancel_conversation(update: Update, context):
    """Отмена диалога"""
    await update.message.reply_text(
        "❌ Операция отменена. Используй /start для возврата в главное меню."
    )
    return ConversationHandler.END


# FastAPI приложение
app = FastAPI(
    title="Oracul Bot Local API",
    description="API для мультимодального бота с локальными моделями",
    version="1.0.0-local",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Oracul Bot Local API",
        "version": "1.0.0-local",
        "status": "running",
        "features": ["local-models", "whisper", "vllm", "privacy-first"]
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    vllm_status = await vllm_service.health_check()
    
    return {
        "status": "healthy",
        "timestamp": "2024-12-26T23:00:00Z",
        "local_models": "loaded",
        "vllm_server": "available" if vllm_status else "unavailable"
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


@app.get("/models")
async def get_models_status():
    """Получить статус локальных моделей"""
    vllm_models = []
    vllm_available = False
    
    try:
        vllm_available = await vllm_service.health_check()
        if vllm_available:
            vllm_models = await vllm_service.get_models()
    except Exception as e:
        logger.error(f"Error getting vLLM models: {e}")
    
    return {
        "text_analysis": {
            "sentiment": "blanchefort/rubert-base-cased-sentiment",
            "emotions": "j-hartmann/emotion-english-distilroberta-base",
            "embeddings": "DeepPavlov/rubert-base-cased-sentence",
            "generation": "ai-forever/rugpt3small_based_on_gpt2"
        },
        "voice_analysis": {
            "transcription": "whisper-base",
            "audio_features": "librosa"
        },
        "vllm": {
            "available": vllm_available,
            "models": vllm_models
        }
    }


if __name__ == "__main__":
    # Запуск в режиме разработки
    if settings.DEBUG:
        uvicorn.run(
            "main_local:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
            log_level="debug"
        )
    else:
        uvicorn.run(
            "main_local:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info"
        )
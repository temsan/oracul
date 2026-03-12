#!/usr/bin/env python3
"""
Скрипт для запуска Oracul Bot
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings, validate_settings
from database.connection import init_database
from main import setup_telegram_bot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    try:
        logger.info("🔮 Запуск Oracul Bot...")
        
        # Проверяем настройки
        try:
            validate_settings()
            logger.info("✅ Настройки проверены")
        except ValueError as e:
            logger.error(f"❌ Ошибка настроек: {e}")
            return
        
        # Инициализируем базу данных
        try:
            await init_database()
            logger.info("✅ База данных инициализирована")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            return
        
        # Настраиваем и запускаем бота
        try:
            application = await setup_telegram_bot()
            await application.initialize()
            
            logger.info("✅ Telegram Bot инициализирован")
            
            # Запускаем polling
            logger.info("🚀 Запуск polling...")
            await application.run_polling(
                drop_pending_updates=True,
                allowed_updates=['message', 'callback_query']
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
            return
            
    except KeyboardInterrupt:
        logger.info("👋 Остановка бота...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        logger.info("🔮 Oracul Bot остановлен")


if __name__ == "__main__":
    # Проверяем наличие .env файла
    env_file = Path(".env")
    if not env_file.exists():
        logger.error("❌ Файл .env не найден! Скопируйте .env.example в .env и настройте его.")
        sys.exit(1)
    
    # Запускаем бота
    asyncio.run(main())
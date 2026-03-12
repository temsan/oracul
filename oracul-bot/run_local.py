#!/usr/bin/env python3
"""
Скрипт для запуска Oracul Bot с локальными моделями
"""

import asyncio
import logging
import sys
import os
import subprocess
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings, validate_settings
from database.connection import init_database
from services.vllm_service import vllm_service

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_system_requirements():
    """Проверка системных требований"""
    logger.info("🔍 Проверка системных требований...")
    
    # Проверяем Python версию
    python_version = sys.version_info
    if python_version < (3, 11):
        logger.error(f"❌ Требуется Python 3.11+, найден {python_version.major}.{python_version.minor}")
        return False
    
    logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Проверяем CUDA
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"✅ CUDA доступна: {gpu_count} GPU ({gpu_name})")
        else:
            logger.warning("⚠️ CUDA недоступна, будет использоваться CPU")
    except ImportError:
        logger.warning("⚠️ PyTorch не установлен")
    
    # Проверяем доступную память
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        logger.info(f"💾 Доступная память: {memory_gb:.1f} GB")
        
        if memory_gb < 8:
            logger.warning("⚠️ Рекомендуется минимум 8GB RAM для всех моделей")
    except ImportError:
        logger.warning("⚠️ Не удалось проверить память (установите psutil)")
    
    return True


async def check_models():
    """Проверка доступности моделей"""
    logger.info("🧠 Проверка локальных моделей...")
    
    models_status = {
        'whisper': False,
        'transformers': False,
        'torch': False
    }
    
    # Проверяем Whisper
    try:
        import whisper
        models_status['whisper'] = True
        logger.info("✅ Whisper доступен")
    except ImportError:
        logger.error("❌ Whisper не установлен")
    
    # Проверяем Transformers
    try:
        from transformers import pipeline
        models_status['transformers'] = True
        logger.info("✅ Transformers доступен")
    except ImportError:
        logger.error("❌ Transformers не установлен")
    
    # Проверяем PyTorch
    try:
        import torch
        models_status['torch'] = True
        logger.info("✅ PyTorch доступен")
    except ImportError:
        logger.error("❌ PyTorch не установлен")
    
    return all(models_status.values())


async def check_vllm_server():
    """Проверка vLLM сервера"""
    logger.info("⚡ Проверка vLLM сервера...")
    
    try:
        is_available = await vllm_service.health_check()
        
        if is_available:
            models = await vllm_service.get_models()
            logger.info(f"✅ vLLM сервер доступен ({len(models)} моделей)")
            return True
        else:
            logger.warning("⚠️ vLLM сервер недоступен")
            logger.info("💡 Для запуска vLLM сервера:")
            logger.info("   pip install vllm")
            logger.info("   python -m vllm.entrypoints.api_server --model microsoft/DialoGPT-medium")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Ошибка проверки vLLM: {e}")
        return False


async def download_models():
    """Предварительная загрузка моделей"""
    logger.info("📥 Загрузка локальных моделей...")
    
    try:
        # Загружаем Whisper
        import whisper
        logger.info("📥 Загружаем Whisper base...")
        whisper.load_model("base")
        logger.info("✅ Whisper base загружен")
        
        # Загружаем модели для анализа текста
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        models_to_download = [
            "blanchefort/rubert-base-cased-sentiment",
            "j-hartmann/emotion-english-distilroberta-base",
            "DeepPavlov/rubert-base-cased-sentence"
        ]
        
        for model_name in models_to_download:
            try:
                logger.info(f"📥 Загружаем {model_name}...")
                AutoTokenizer.from_pretrained(model_name)
                AutoModelForSequenceClassification.from_pretrained(model_name)
                logger.info(f"✅ {model_name} загружен")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось загрузить {model_name}: {e}")
        
        logger.info("✅ Загрузка моделей завершена")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки моделей: {e}")
        return False


async def start_local_bot():
    """Запуск локального бота"""
    logger.info("🚀 Запуск Oracul Bot с локальными моделями...")
    
    try:
        # Импортируем и запускаем основное приложение
        from main_local import app
        import uvicorn
        
        # Запускаем сервер
        config = uvicorn.Config(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info" if not settings.DEBUG else "debug"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        return False


async def main():
    """Главная функция запуска"""
    try:
        logger.info("🔮 Запуск Oracul Bot Local Edition...")
        
        # Проверяем настройки
        try:
            validate_settings()
            logger.info("✅ Настройки проверены")
        except ValueError as e:
            logger.error(f"❌ Ошибка настроек: {e}")
            return
        
        # Проверяем системные требования
        if not await check_system_requirements():
            logger.error("❌ Системные требования не выполнены")
            return
        
        # Проверяем модели
        if not await check_models():
            logger.error("❌ Не все модели доступны")
            logger.info("💡 Установите зависимости: pip install -r requirements_local.txt")
            return
        
        # Инициализируем базу данных
        try:
            await init_database()
            logger.info("✅ База данных инициализирована")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            return
        
        # Проверяем vLLM (опционально)
        vllm_available = await check_vllm_server()
        if not vllm_available:
            logger.info("ℹ️ Бот будет работать без vLLM (ограниченная функциональность)")
        
        # Загружаем модели
        if not await download_models():
            logger.warning("⚠️ Не все модели загружены, но продолжаем запуск")
        
        # Запускаем бота
        await start_local_bot()
        
    except KeyboardInterrupt:
        logger.info("👋 Остановка бота...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        logger.info("🔮 Oracul Bot Local остановлен")


if __name__ == "__main__":
    # Проверяем наличие .env файла
    env_file = Path(".env")
    if not env_file.exists():
        logger.error("❌ Файл .env не найден! Скопируйте .env.example в .env и настройте его.")
        sys.exit(1)
    
    # Запускаем бота
    asyncio.run(main())
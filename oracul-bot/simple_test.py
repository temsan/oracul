#!/usr/bin/env python3
"""
Простое тестирование основных компонентов Oracul Bot
"""

import asyncio
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings


async def test_settings():
    """Тест настроек"""
    print("🧪 Тестирование настроек...")
    
    required_settings = [
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY',
        'DATABASE_URL'
    ]
    
    missing = []
    configured = []
    
    for setting in required_settings:
        value = getattr(settings, setting, None)
        if not value or value == f"YOUR_{setting}_HERE":
            missing.append(setting)
        else:
            configured.append(setting)
    
    if configured:
        print(f"✅ Настроены: {', '.join(configured)}")
    
    if missing:
        print(f"❌ Требуют настройки: {', '.join(missing)}")
        print("\n📝 Инструкции по настройке:")
        for setting in missing:
            if setting == 'TELEGRAM_BOT_TOKEN':
                print("   • Создайте бота через @BotFather в Telegram")
            elif setting == 'OPENAI_API_KEY':
                print("   • Получите ключ на https://platform.openai.com")
            elif setting == 'DATABASE_URL':
                print("   • Установите PostgreSQL и создайте базу данных")
    else:
        print("✅ Все обязательные настройки присутствуют!")
    
    # Проверяем дополнительные настройки
    optional_settings = [
        'TELEGRAM_API_ID',
        'TELEGRAM_API_HASH',
        'REDIS_URL'
    ]
    
    print("\n🔧 Дополнительные настройки:")
    for setting in optional_settings:
        value = getattr(settings, setting, None)
        if value and value.strip():
            print(f"✅ {setting} настроен")
        else:
            print(f"⚠️ {setting} не настроен (опционально)")
            if setting.startswith('TELEGRAM_API'):
                print("   └─ Нужен для анализа каналов")


async def test_text_analyzer_basic():
    """Базовый тест анализатора текста"""
    print("\n🧪 Тестирование анализатора текста...")
    
    try:
        from analyzers.text_analyzer import TextAnalyzer
        
        analyzer = TextAnalyzer()
        
        # Простой тест без OpenAI
        test_text = "Привет! Сегодня отличное настроение!"
        
        # Тестируем только базовые функции
        cleaned = analyzer._preprocess_text(test_text)
        print(f"✅ Предобработка текста работает: '{cleaned[:30]}...'")
        
        # Тестируем анализ тональности
        sentiment = await analyzer._analyze_sentiment(test_text)
        print(f"✅ Анализ тональности: {sentiment.get('label', 'N/A')}")
        
        # Тестируем анализ эмоций
        emotions = await analyzer._analyze_emotions(test_text)
        print(f"✅ Анализ эмоций: {list(emotions.keys())[:3]}")
        
        print("✅ Базовые функции анализатора текста работают")
        
    except Exception as e:
        print(f"❌ Ошибка анализатора текста: {e}")


async def test_database_models():
    """Тест моделей базы данных"""
    print("\n🧪 Тестирование моделей базы данных...")
    
    try:
        from models.database import User, Analysis, SubscriptionType, AnalysisType
        
        # Создаем тестового пользователя
        user = User(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            subscription_type=SubscriptionType.FREE
        )
        
        print(f"✅ Модель User создана: {user}")
        print(f"✅ Проверка Premium статуса: {user.is_premium}")
        print(f"✅ Проверка возможности анализа: {user.can_analyze()}")
        
        # Создаем тестовый анализ
        analysis = Analysis(
            user_id=1,
            analysis_type=AnalysisType.TEXT,
            input_data={"text": "test"},
            results={"sentiment": "positive"},
            summary="Тестовый анализ"
        )
        
        print(f"✅ Модель Analysis создана: {analysis}")
        print("✅ Модели базы данных работают корректно")
        
    except Exception as e:
        print(f"❌ Ошибка моделей БД: {e}")


async def test_bot_handlers_basic():
    """Базовый тест обработчиков бота"""
    print("\n🧪 Тестирование обработчиков бота...")
    
    try:
        from bot.handlers import BotHandlers
        from services.analysis_service import AnalysisService
        from services.channel_service import ChannelService
        
        # Создаем сервисы
        analysis_service = AnalysisService()
        channel_service = ChannelService()
        
        # Создаем обработчики
        handlers = BotHandlers(analysis_service, channel_service)
        
        print("✅ Обработчики бота созданы успешно")
        
        # Тестируем форматирование
        test_analysis = {
            'sentiment': {'label': 'positive', 'confidence': 0.8},
            'emotions': {'joy': 0.7, 'excitement': 0.5},
            'recommendations': ['Отличное настроение!']
        }
        
        formatted = handlers.format_text_analysis(test_analysis)
        print(f"✅ Форматирование анализа работает: {len(formatted)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка обработчиков бота: {e}")


async def main():
    """Главная функция тестирования"""
    print("🔮 Простое тестирование компонентов Oracul Bot\n")
    
    # Тестируем настройки
    await test_settings()
    
    # Тестируем модели БД
    await test_database_models()
    
    # Тестируем анализатор текста
    await test_text_analyzer_basic()
    
    # Тестируем обработчики бота
    await test_bot_handlers_basic()
    
    print("\n🏁 Простое тестирование завершено!")
    print("\n📋 Следующие шаги:")
    print("1. Настройте отсутствующие параметры в .env файле")
    print("2. Установите и настройте PostgreSQL")
    print("3. Запустите: python run_bot.py")


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Минимальный тест бота без БД
"""

import asyncio
import sys
import logging
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.local_text_analyzer import LocalTextAnalyzer
from analyzers.local_voice_analyzer import LocalVoiceAnalyzer
from services.local_analysis_service import LocalAnalysisService

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_analysis_service():
    """Тест сервиса анализа"""
    print("🔮 Тестирование LocalAnalysisService...")
    
    try:
        service = LocalAnalysisService()
        
        # Тест анализа текста
        text_result = await service.analyze_text(
            12345,
            "Привет! Сегодня отличный день, много планов и хорошее настроение!"
        )
        
        if text_result.get('success'):
            print("✅ Анализ текста через сервис работает")
            print(f"📊 Результат: {text_result.get('summary', 'Нет резюме')}")
        else:
            print(f"❌ Ошибка анализа текста: {text_result.get('error')}")
            return False
        
        print("✅ Сервис анализа работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования сервиса: {e}")
        return False


async def test_bot_handlers():
    """Тест обработчиков бота (без Telegram)"""
    print("\n🤖 Тестирование обработчиков бота...")
    
    try:
        from bot.local_handlers import LocalBotHandlers
        from services.channel_service import ChannelService
        
        # Создаем сервисы
        analysis_service = LocalAnalysisService()
        channel_service = ChannelService()
        
        # Создаем обработчики
        handlers = LocalBotHandlers(analysis_service, channel_service)
        
        print("✅ Обработчики бота инициализированы")
        
        # Тест создания меню
        from telegram import InlineKeyboardMarkup
        
        # Проверяем, что методы создания меню работают
        if hasattr(handlers, '_create_main_menu'):
            menu = handlers._create_main_menu()
            if isinstance(menu, InlineKeyboardMarkup):
                print("✅ Главное меню создается корректно")
            else:
                print("❌ Ошибка создания главного меню")
                return False
        
        print("✅ Обработчики бота работают корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования обработчиков: {e}")
        return False


async def test_integration():
    """Интеграционный тест всей системы"""
    print("\n🔗 Интеграционный тест системы...")
    
    try:
        # Создаем все компоненты
        text_analyzer = LocalTextAnalyzer()
        voice_analyzer = LocalVoiceAnalyzer()
        analysis_service = LocalAnalysisService()
        
        # Тест полного цикла анализа
        test_text = "Сегодня сложный день на работе, но я справляюсь и учусь новому."
        
        # Анализ через анализатор
        direct_result = await text_analyzer.analyze(test_text)
        
        # Анализ через сервис
        service_result = await analysis_service.analyze_text(12345, test_text)
        
        if direct_result.get('success') and service_result.get('success'):
            print("✅ Интеграция анализатора и сервиса работает")
            
            # Сравниваем результаты
            direct_sentiment = direct_result.get('sentiment', {}).get('label', 'unknown')
            service_summary = service_result.get('summary', '')
            
            print(f"📊 Прямой анализ: тональность {direct_sentiment}")
            print(f"🔮 Через сервис: {service_summary[:100]}...")
            
        else:
            print("❌ Ошибка интеграции")
            return False
        
        print("✅ Интеграционный тест пройден")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграционного теста: {e}")
        return False


async def main():
    """Главная функция тестирования"""
    print("🔮 Минимальный тест Oracul Bot Local")
    print("=" * 50)
    
    # Проверяем системные требования
    print(f"🐍 Python: {sys.version}")
    
    try:
        import torch
        print(f"🔥 PyTorch: {torch.__version__}")
        print(f"🎮 CUDA: {'Доступна' if torch.cuda.is_available() else 'Недоступна'}")
    except ImportError:
        print("❌ PyTorch не установлен")
    
    print("\n" + "=" * 50)
    
    # Запускаем тесты
    results = []
    
    # Тест сервиса анализа
    service_result = await test_analysis_service()
    results.append(("Analysis Service", service_result))
    
    # Тест обработчиков бота
    handlers_result = await test_bot_handlers()
    results.append(("Bot Handlers", handlers_result))
    
    # Интеграционный тест
    integration_result = await test_integration()
    results.append(("Integration Test", integration_result))
    
    # Итоги
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:")
    
    for test_name, result in results:
        status = "✅ Пройден" if result else "❌ Не пройден"
        print(f"  {test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n🎯 Итого: {success_count}/{total_count} тестов пройдено")
    
    if success_count == total_count:
        print("🎉 Все тесты пройдены! Система готова к работе.")
        print("\n💡 Для полного запуска:")
        print("1. Настройте TELEGRAM_BOT_TOKEN в .env")
        print("2. Запустите PostgreSQL (или используйте Docker)")
        print("3. Опционально запустите vLLM сервер")
        print("4. Выполните: python run_local.py")
    elif success_count > 0:
        print("⚠️ Система частично готова. Некоторые функции могут быть ограничены.")
    else:
        print("❌ Система не готова. Проверьте установку зависимостей.")


if __name__ == "__main__":
    asyncio.run(main())
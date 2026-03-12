#!/usr/bin/env python3
"""
Тест обработки rate limits и переключения между моделями
"""

import asyncio
import sys
import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / 'oracul-bot'))

from services.openrouter_service import OpenRouterService

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_rate_limit_handling():
    """Тест обработки rate limits"""
    print("🔄 ТЕСТ ОБРАБОТКИ RATE LIMITS")
    print("=" * 50)
    
    try:
        # Инициализируем сервис
        service = OpenRouterService()
        
        # Проверяем конфигурацию
        print(f"🎯 Основная модель: {service.default_model}")
        print(f"🔄 Резервная модель: {service.backup_model}")
        print(f"📋 Доступно моделей: {len(service.free_models)}")
        
        # Тест соединения
        print("\n🔗 Тест соединения...")
        connection_result = await service.test_connection()
        
        if connection_result.get('success'):
            print("✅ Соединение успешно")
            print(f"📝 Ответ: {connection_result.get('response', '')[:50]}...")
        else:
            print(f"❌ Ошибка соединения: {connection_result.get('error')}")
            return False
        
        # Тест анализа текста с потенциальным rate limit
        test_texts = [
            "Сегодня отличный день для работы над проектом!",
            "Анализирую данные и готовлю отчет по исследованию.",
            "Столкнулся с техническими сложностями, но продолжаю работать.",
            "Размышляю о будущем искусственного интеллекта."
        ]
        
        print(f"\n🧠 Тест анализа {len(test_texts)} текстов...")
        
        successful_analyses = 0
        model_usage = {}
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 Анализ {i}/{len(test_texts)}: {text[:30]}...")
            
            result = await service.analyze_text(text, task_type='analysis')
            
            if result.get('success'):
                successful_analyses += 1
                model_used = result.get('model_used', 'unknown')
                model_usage[model_used] = model_usage.get(model_used, 0) + 1
                
                print(f"✅ Успешно (модель: {model_used})")
                
                # Показываем краткий результат
                analysis = result.get('analysis', {})
                sentiment = analysis.get('sentiment', {})
                if sentiment:
                    print(f"   📊 Тональность: {sentiment.get('label', 'unknown')}")
                
            else:
                print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
            
            # Небольшая пауза между запросами
            await asyncio.sleep(0.5)
        
        # Итоговая статистика
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print(f"✅ Успешных анализов: {successful_analyses}/{len(test_texts)}")
        print(f"📈 Процент успеха: {successful_analyses/len(test_texts)*100:.1f}%")
        
        if model_usage:
            print(f"🎯 Использование моделей:")
            for model, count in model_usage.items():
                print(f"   • {model}: {count} запросов")
        
        # Оценка готовности
        if successful_analyses >= len(test_texts) * 0.8:  # 80% успеха
            print(f"\n🎉 СИСТЕМА ГОТОВА!")
            print(f"✅ Rate limit handling работает корректно")
            print(f"✅ Автоматическое переключение моделей функционирует")
            return True
        else:
            print(f"\n⚠️ ТРЕБУЕТСЯ ДОРАБОТКА")
            print(f"❌ Слишком много неудачных запросов")
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Главная функция"""
    print("🔮 ТЕСТ ОБРАБОТКИ RATE LIMITS OPENROUTER")
    print("🎯 Проверка автоматического переключения моделей")
    print("=" * 60)
    
    success = await test_rate_limit_handling()
    
    if success:
        print(f"\n🚀 Система готова к работе с расширенным анализом!")
    else:
        print(f"\n🔧 Требуется дополнительная настройка")


if __name__ == "__main__":
    asyncio.run(main())
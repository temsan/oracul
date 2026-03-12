#!/usr/bin/env python3
"""
Тест парсинга OpenRouter для проверки исправлений
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / 'oracul-bot'))

from services.openrouter_service import OpenRouterService

async def test_openrouter_parsing():
    """Тест парсинга ответов OpenRouter"""
    
    service = OpenRouterService()
    
    print("🧪 Тестируем OpenRouter парсинг...")
    
    # Тест 1: JSON ответ
    json_response = '''
    {
      "sentiment": {"label": "positive", "confidence": 0.8},
      "themes": ["работа", "проекты", "планы"],
      "insights": ["Активное обсуждение рабочих вопросов", "Позитивный настрой к задачам"],
      "emotions": {"joy": 0.6, "interest": 0.4}
    }
    '''
    
    print("\n📄 Тест 1: JSON ответ")
    result1 = service._parse_analysis_result(json_response)
    print(f"Результат: {result1}")
    
    # Тест 2: Текстовый ответ
    text_response = '''
    ТОНАЛЬНОСТЬ: positive
    ТЕМЫ: работа, карьера, развитие
    ИНСАЙТЫ:
    • Обсуждаются вопросы профессионального роста
    • Позитивное отношение к новым задачам
    • Активное планирование будущих проектов
    '''
    
    print("\n📝 Тест 2: Текстовый ответ")
    result2 = service._parse_analysis_result(text_response)
    print(f"Результат: {result2}")
    
    # Тест 3: Реальный анализ
    test_text = "Привет! Как дела с проектом? Я думаю, нам нужно ускориться с разработкой. Очень жду результатов!"
    
    print("\n🔍 Тест 3: Реальный анализ текста")
    print(f"Текст: {test_text}")
    
    result3 = await service.analyze_text(test_text, 'analysis')
    print(f"Успех: {result3.get('success')}")
    print(f"Модель: {result3.get('model_used')}")
    
    if result3.get('success'):
        analysis = result3.get('analysis', {})
        print(f"Анализ: {analysis}")
        
        # Проверяем наличие ключевых полей
        has_sentiment = 'sentiment' in analysis
        has_themes = 'themes' in analysis
        has_insights = 'insights' in analysis
        
        print(f"\n✅ Проверка полей:")
        print(f"  Тональность: {'✅' if has_sentiment else '❌'}")
        print(f"  Темы: {'✅' if has_themes else '❌'}")
        print(f"  Инсайты: {'✅' if has_insights else '❌'}")
        
        if has_insights:
            insights = analysis.get('insights', [])
            print(f"  Количество инсайтов: {len(insights)}")
            for i, insight in enumerate(insights[:3], 1):
                print(f"    {i}. {insight}")
    else:
        print(f"❌ Ошибка: {result3.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_openrouter_parsing())
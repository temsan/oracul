#!/usr/bin/env python3
"""
Исправленный тест современных моделей с OpenRouter интеграцией
Использует настроенные API ключи из .env файла
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


class FixedModernModelsTest:
    """Исправленное тестирование современных моделей"""
    
    def __init__(self):
        self.openrouter_service = None
    
    async def initialize(self):
        """Инициализация сервисов"""
        try:
            print("🚀 Инициализация современных AI-моделей...")
            
            # Проверяем переменные окружения
            api_key = os.getenv('OPENROUTER_API_KEY')
            if api_key:
                print(f"🔑 OpenRouter API ключ найден: {api_key[:20]}...")
            else:
                print("⚠️ OpenRouter API ключ не найден в .env")
                return False
            
            # OpenRouter сервис
            self.openrouter_service = OpenRouterService()
            
            print("✅ Инициализация завершена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def test_openrouter_connection(self):
        """Тест соединения с OpenRouter"""
        print("\n🌐 ТЕСТ OPENROUTER СОЕДИНЕНИЯ")
        print("=" * 50)
        
        try:
            # Проверяем API ключ
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                print("⚠️ OPENROUTER_API_KEY не найден в .env файле")
                return False
            
            print(f"🔑 API ключ загружен: {api_key[:20]}...")
            
            # Тест соединения
            connection_result = await self.openrouter_service.test_connection()
            
            if connection_result.get('success'):
                print("✅ Соединение с OpenRouter успешно!")
                print(f"🤖 Протестированная модель: {connection_result.get('model_tested')}")
                print(f"📝 Ответ: {connection_result.get('response', '')[:100]}...")
                return True
            else:
                print(f"❌ Ошибка соединения: {connection_result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Критическая ошибка теста соединения: {e}")
            return False
    
    async def test_openrouter_analysis(self):
        """Тест анализа через OpenRouter"""
        print("\n🤖 ТЕСТ OPENROUTER АНАЛИЗА")
        print("=" * 50)
        
        test_texts = [
            {
                'name': 'Эмоциональный анализ',
                'text': 'Сегодня отличный день! Много планов и хорошее настроение. Чувствую себя очень энергично и готов к новым свершениям!',
                'task': 'analysis'
            },
            {
                'name': 'Грустный текст', 
                'text': 'Мне очень грустно и одиноко. Ничего не получается, все идет не так как планировал. Чувствую разочарование и усталость.',
                'task': 'analysis'
            },
            {
                'name': 'Технический анализ',
                'text': 'Архитектура нейронных сетей на основе трансформеров показывает превосходные результаты в задачах обработки естественного языка. Механизм внимания позволяет модели фокусироваться на важных частях входной последовательности.',
                'task': 'reasoning'
            },
            {
                'name': 'Смешанные эмоции',
                'text': 'Работа над проектом идет хорошо, но есть некоторые сложности. Команда старается, хотя иногда возникают разногласия. В целом настроен оптимистично, но беспокоюсь о дедлайнах.',
                'task': 'analysis'
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_texts, 1):
            print(f"\n--- OpenRouter Тест {i}: {test_case['name']} ---")
            print(f"📝 Текст: {test_case['text'][:80]}...")
            print(f"🎯 Задача: {test_case['task']}")
            
            try:
                result = await self.openrouter_service.analyze_text(
                    test_case['text'], 
                    test_case['task']
                )
                
                if result.get('success'):
                    print("✅ OpenRouter анализ успешен")
                    print(f"🤖 Модель: {result.get('model_used')}")
                    
                    analysis = result.get('analysis', {})
                    
                    # Показываем результаты
                    if 'sentiment' in analysis:
                        sent = analysis['sentiment']
                        print(f"📊 Тональность: {sent.get('label')} ({sent.get('confidence', 0)*100:.1f}%)")
                    
                    if 'emotions' in analysis:
                        emotions = analysis['emotions']
                        if isinstance(emotions, dict):
                            top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
                            emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions if s > 0.1])
                            if emotion_str:
                                print(f"😊 Эмоции: {emotion_str}")
                    
                    if 'insights' in analysis:
                        insights = analysis['insights']
                        if isinstance(insights, list) and insights:
                            print(f"💡 Инсайты: {'; '.join(insights[:2])}")
                    
                    if 'themes' in analysis:
                        themes = analysis['themes']
                        if isinstance(themes, list) and themes:
                            print(f"🎯 Темы: {', '.join(themes[:3])}")
                    
                    if 'personality' in analysis:
                        personality = analysis['personality']
                        if isinstance(personality, dict):
                            top_traits = sorted(personality.items(), key=lambda x: x[1], reverse=True)[:2]
                            trait_str = ', '.join([f"{t}: {s*100:.1f}%" for t, s in top_traits if s > 0.5])
                            if trait_str:
                                print(f"👤 Личность: {trait_str}")
                    
                    results.append({
                        'test': test_case['name'],
                        'success': True,
                        'model': result.get('model_used'),
                        'analysis': analysis
                    })
                    
                else:
                    print(f"❌ Ошибка OpenRouter: {result.get('error')}")
                    results.append({
                        'test': test_case['name'],
                        'success': False,
                        'error': result.get('error')
                    })
                    
            except Exception as e:
                print(f"❌ Критическая ошибка OpenRouter: {e}")
                results.append({
                    'test': test_case['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def test_different_models(self):
        """Тест разных моделей OpenRouter"""
        print("\n🎭 ТЕСТ РАЗНЫХ МОДЕЛЕЙ OPENROUTER")
        print("=" * 50)
        
        test_text = "Я очень волнуюсь перед важной презентацией завтра. С одной стороны, я хорошо подготовился и уверен в материале. С другой стороны, боюсь, что что-то пойдет не так."
        
        # Тестируем разные модели
        models_to_test = [
            ("meta-llama/llama-3.2-3b-instruct:free", "Meta Llama 3.2"),
            ("microsoft/phi-3-mini-128k-instruct:free", "Microsoft Phi-3"),
            ("qwen/qwen-2-7b-instruct:free", "Alibaba Qwen 2"),
            ("mistralai/mistral-7b-instruct:free", "Mistral 7B")
        ]
        
        results = []
        
        for model_id, model_name in models_to_test:
            print(f"\n--- Тест модели: {model_name} ---")
            print(f"🤖 ID: {model_id}")
            
            try:
                # Прямой запрос к модели
                result = await self.openrouter_service._make_request(
                    model=model_id,
                    prompt=f"Проанализируй эмоциональное состояние автора этого текста: '{test_text}'. Определи основные эмоции и дай краткие рекомендации.",
                    max_tokens=500
                )
                
                if result.get('success'):
                    print("✅ Модель работает")
                    content = result.get('content', '')
                    print(f"📝 Ответ: {content[:200]}...")
                    
                    usage = result.get('usage', {})
                    if usage:
                        print(f"📊 Токены: {usage.get('total_tokens', 'N/A')}")
                    
                    results.append({
                        'model': model_name,
                        'model_id': model_id,
                        'success': True,
                        'response_length': len(content),
                        'usage': usage
                    })
                else:
                    print(f"❌ Ошибка: {result.get('error')}")
                    results.append({
                        'model': model_name,
                        'model_id': model_id,
                        'success': False,
                        'error': result.get('error')
                    })
                    
            except Exception as e:
                print(f"❌ Критическая ошибка: {e}")
                results.append({
                    'model': model_name,
                    'model_id': model_id,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def generate_summary_report(self, connection_success, analysis_results, model_results):
        """Генерация итогового отчета"""
        print("\n📊 ИТОГОВЫЙ ОТЧЕТ СОВРЕМЕННЫХ МОДЕЛЕЙ")
        print("=" * 60)
        
        # OpenRouter соединение
        print(f"🌐 OPENROUTER СОЕДИНЕНИЕ:")
        print(f"  • Статус: {'✅ Успешно' if connection_success else '❌ Ошибка'}")
        
        # Анализ текста
        analysis_success = len([r for r in analysis_results if r.get('success')])
        analysis_total = len(analysis_results)
        
        print(f"\n🤖 АНАЛИЗ ТЕКСТА:")
        print(f"  • Успешных тестов: {analysis_success}/{analysis_total}")
        if analysis_total > 0:
            print(f"  • Успешность: {analysis_success/analysis_total*100:.1f}%")
        else:
            print(f"  • Успешность: N/A (тесты не запускались)")
        
        if analysis_success > 0:
            models_used = set()
            for result in analysis_results:
                if result.get('success') and result.get('model'):
                    models_used.add(result['model'])
            
            print(f"  • Протестированные модели: {len(models_used)}")
            for model in models_used:
                print(f"    - {model}")
        
        # Тест моделей
        model_success = len([r for r in model_results if r.get('success')])
        model_total = len(model_results)
        
        print(f"\n🎭 ТЕСТ МОДЕЛЕЙ:")
        print(f"  • Успешных моделей: {model_success}/{model_total}")
        if model_total > 0:
            print(f"  • Успешность: {model_success/model_total*100:.1f}%")
        else:
            print(f"  • Успешность: N/A (тесты не запускались)")
        
        if model_success > 0:
            print(f"  • Работающие модели:")
            for result in model_results:
                if result.get('success'):
                    model_name = result.get('model', 'Unknown')
                    response_len = result.get('response_length', 0)
                    print(f"    ✅ {model_name} (ответ: {response_len} символов)")
        
        # Общая оценка
        total_success = (1 if connection_success else 0) + analysis_success + model_success
        total_tests = 1 + analysis_total + model_total
        
        if total_tests > 0:
            overall_score = total_success / total_tests
        else:
            overall_score = 0
        
        print(f"\n🏆 ОБЩАЯ ОЦЕНКА:")
        print(f"  • Успешных тестов: {total_success}/{total_tests}")
        print(f"  • Общий балл: {overall_score*100:.1f}%")
        
        if overall_score >= 0.8:
            print(f"  • Статус: 🎉 ОТЛИЧНО - OpenRouter полностью готов!")
        elif overall_score >= 0.6:
            print(f"  • Статус: ✅ ХОРОШО - Основные функции работают")
        else:
            print(f"  • Статус: ⚠️ ТРЕБУЕТ НАСТРОЙКИ")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        if connection_success:
            print(f"  ✅ OpenRouter соединение работает отлично")
        else:
            print(f"  ⚠️ Проверьте настройки OpenRouter API ключа")
        
        if analysis_success == analysis_total:
            print(f"  ✅ Анализ текста работает идеально")
        elif analysis_success > 0:
            print(f"  ⚡ Анализ текста работает частично")
        else:
            print(f"  ❌ Анализ текста требует исправления")
        
        if model_success == model_total:
            print(f"  ✅ Все модели доступны и работают")
        elif model_success > 0:
            print(f"  ⚡ Часть моделей работает, используйте рабочие")
        else:
            print(f"  ❌ Модели недоступны, проверьте API лимиты")
        
        # Практические советы
        print(f"\n🚀 ПРАКТИЧЕСКИЕ СОВЕТЫ:")
        print(f"  • Используйте google/gemini-flash-1.5 для быстрого анализа")
        print(f"  • microsoft/phi-3-mini-128k-instruct:free для длинных текстов")
        print(f"  • meta-llama/llama-3.2-3b-instruct:free для творческих задач")
        print(f"  • Мониторьте использование бесплатных лимитов")


async def main():
    """Главная функция тестирования современных моделей"""
    print("🚀 ТЕСТИРОВАНИЕ СОВРЕМЕННЫХ AI-МОДЕЛЕЙ 2024 (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("🔮 Oracul Bot - Modern Models Integration Test")
    print("=" * 70)
    
    tester = FixedModernModelsTest()
    
    try:
        # Инициализация
        if not await tester.initialize():
            print("❌ Ошибка инициализации")
            return
        
        # Тест OpenRouter соединения
        connection_success = await tester.test_openrouter_connection()
        
        # Тест OpenRouter анализа (если соединение работает)
        analysis_results = []
        if connection_success:
            analysis_results = await tester.test_openrouter_analysis()
        
        # Тест разных моделей
        model_results = []
        if connection_success:
            model_results = await tester.test_different_models()
        
        # Генерация итогового отчета
        tester.generate_summary_report(connection_success, analysis_results, model_results)
        
        print(f"\n🎯 ТЕСТИРОВАНИЕ СОВРЕМЕННЫХ МОДЕЛЕЙ ЗАВЕРШЕНО!")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
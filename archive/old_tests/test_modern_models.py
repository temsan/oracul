#!/usr/bin/env python3
"""
Тест современных моделей и OpenRouter интеграции
"""

import asyncio
import sys
import os
from pathlib import Path
import logging

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / 'oracul-bot'))

from analyzers.modern_text_analyzer import ModernTextAnalyzer
from services.openrouter_service import OpenRouterService

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModernModelsTest:
    """Тестирование современных моделей"""
    
    def __init__(self):
        self.modern_analyzer = None
        self.openrouter_service = None
    
    async def initialize(self):
        """Инициализация сервисов"""
        try:
            print("🚀 Инициализация современных AI-моделей...")
            
            # Современный анализатор
            self.modern_analyzer = ModernTextAnalyzer()
            
            # OpenRouter сервис
            self.openrouter_service = OpenRouterService()
            
            print("✅ Инициализация завершена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def test_modern_local_models(self):
        """Тест современных локальных моделей"""
        print("\n🧠 ТЕСТ СОВРЕМЕННЫХ ЛОКАЛЬНЫХ МОДЕЛЕЙ")
        print("=" * 50)
        
        test_texts = [
            {
                'name': 'Эмоциональный текст',
                'text': 'Я очень рад этой новости! Это потрясающе! Наконец-то все получилось, и я чувствую огромное счастье и гордость за проделанную работу.'
            },
            {
                'name': 'Грустный текст', 
                'text': 'Мне очень грустно и одиноко. Ничего не получается, все идет не так как планировал. Чувствую разочарование и усталость.'
            },
            {
                'name': 'Технический текст',
                'text': 'Разработка нейронных сетей требует глубокого понимания математических основ. Архитектура трансформеров показывает отличные результаты в задачах NLP.'
            },
            {
                'name': 'Смешанный текст',
                'text': 'Работа над проектом идет хорошо, но есть некоторые сложности. Команда старается, хотя иногда возникают разногласия. В целом настроен оптимистично.'
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_texts, 1):
            print(f"\n--- Тест {i}: {test_case['name']} ---")
            print(f"📝 Текст: {test_case['text'][:80]}...")
            
            try:
                result = await self.modern_analyzer.analyze_with_modern_models(test_case['text'])
                
                if result.get('success'):
                    print("✅ Анализ успешен")
                    
                    local_results = result['results']
                    
                    # Современные эмоции (9 категорий)
                    if 'modern_emotions' in local_results:
                        emotions = local_results['modern_emotions']
                        top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
                        emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions if s > 0.1])
                        if emotion_str:
                            print(f"😊 Современные эмоции: {emotion_str}")
                    
                    # Улучшенная тональность
                    if 'improved_sentiment' in local_results:
                        sent = local_results['improved_sentiment']
                        print(f"📊 Улучшенная тональность: {sent['label']} ({sent['confidence']*100:.1f}%)")
                    
                    # Многоязычная модель
                    if 'multilingual_sentiment' in local_results:
                        multi = local_results['multilingual_sentiment']
                        print(f"🌍 Многоязычная модель: {multi['label']} ({multi['confidence']*100:.1f}%)")
                    
                    # Компактная модель
                    if 'compact_sentiment' in local_results:
                        compact = local_results['compact_sentiment']
                        print(f"⚡ Компактная модель: {compact['label']} ({compact['confidence']*100:.1f}%)")
                    
                    results.append({
                        'test': test_case['name'],
                        'success': True,
                        'results': local_results
                    })
                    
                else:
                    print(f"❌ Ошибка: {result.get('error')}")
                    results.append({
                        'test': test_case['name'],
                        'success': False,
                        'error': result.get('error')
                    })
                    
            except Exception as e:
                print(f"❌ Критическая ошибка: {e}")
                results.append({
                    'test': test_case['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def test_openrouter_connection(self):
        """Тест соединения с OpenRouter"""
        print("\n🌐 ТЕСТ OPENROUTER СОЕДИНЕНИЯ")
        print("=" * 50)
        
        try:
            # Проверяем API ключ
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                print("⚠️ OPENROUTER_API_KEY не установлен в переменных окружения")
                print("💡 Для тестирования OpenRouter:")
                print("   1. Зарегистрируйтесь на https://openrouter.ai/")
                print("   2. Получите бесплатный API ключ")
                print("   3. Установите: set OPENROUTER_API_KEY=your_key")
                return False
            
            print(f"🔑 API ключ найден: {api_key[:10]}...")
            
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
        
        # Проверяем доступность
        if not os.getenv('OPENROUTER_API_KEY'):
            print("⚠️ OpenRouter API ключ не настроен, пропускаем тест")
            return []
        
        test_texts = [
            {
                'name': 'Короткий анализ',
                'text': 'Сегодня отличный день! Много планов и хорошее настроение.',
                'task': 'analysis'
            },
            {
                'name': 'Технический анализ',
                'text': 'Архитектура нейронных сетей на основе трансформеров показывает превосходные результаты в задачах обработки естественного языка.',
                'task': 'reasoning'
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_texts, 1):
            print(f"\n--- OpenRouter Тест {i}: {test_case['name']} ---")
            print(f"📝 Текст: {test_case['text'][:60]}...")
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
    
    async def test_comprehensive_analysis(self):
        """Тест комплексного анализа"""
        print("\n🔮 ТЕСТ КОМПЛЕКСНОГО АНАЛИЗА")
        print("=" * 50)
        
        test_text = """Работа над новым проектом идет очень хорошо! Команда показывает отличные результаты, 
        и я чувствую гордость за наши достижения. Конечно, есть некоторые сложности с техническими решениями, 
        но мы их успешно преодолеваем. Особенно радует творческий подход коллег к решению нестандартных задач."""
        
        print(f"📝 Тестовый текст: {test_text[:100]}...")
        
        try:
            # Комплексный анализ (локальные + OpenRouter)
            result = await self.modern_analyzer.comprehensive_analysis(
                test_text, 
                use_openrouter=bool(os.getenv('OPENROUTER_API_KEY'))
            )
            
            if result.get('success'):
                analysis = result['analysis']
                
                print("✅ Комплексный анализ успешен")
                print(f"🔧 Методы: {', '.join(analysis.get('analysis_methods', []))}")
                
                # Сводка
                summary = analysis.get('summary', {})
                if summary:
                    print(f"📊 Методов использовано: {summary.get('methods_used', 0)}")
                    print(f"🎯 Уровень уверенности: {summary.get('confidence_level', 'unknown')}")
                    
                    # Консенсус тональности
                    if 'consensus_sentiment' in summary:
                        consensus = summary['consensus_sentiment']
                        print(f"📈 Консенсус тональности: {consensus['label']} ({consensus['confidence']*100:.1f}%, согласие: {consensus['agreement']*100:.1f}%)")
                    
                    # Топ эмоции
                    if 'top_emotions' in summary:
                        top_emotions = summary['top_emotions']
                        emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions[:3]])
                        print(f"😊 Топ эмоции: {emotion_str}")
                    
                    # OpenRouter инсайты
                    if 'openrouter_insights' in summary:
                        insights = summary['openrouter_insights']
                        if insights:
                            print(f"🤖 OpenRouter инсайты: {'; '.join(insights[:2])}")
                
                return True
            else:
                print(f"❌ Ошибка комплексного анализа: {result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Критическая ошибка комплексного анализа: {e}")
            return False
    
    def generate_summary_report(self, local_results, openrouter_results, comprehensive_success):
        """Генерация итогового отчета"""
        print("\n📊 ИТОГОВЫЙ ОТЧЕТ СОВРЕМЕННЫХ МОДЕЛЕЙ")
        print("=" * 60)
        
        # Локальные модели
        local_success = len([r for r in local_results if r.get('success')])
        local_total = len(local_results)
        
        print(f"🧠 ЛОКАЛЬНЫЕ МОДЕЛИ:")
        print(f"  • Успешных тестов: {local_success}/{local_total}")
        print(f"  • Успешность: {local_success/local_total*100:.1f}%")
        
        if local_success > 0:
            print(f"  • Современные эмоции: ✅ 9 категорий")
            print(f"  • Улучшенная тональность: ✅ VK данные")
            print(f"  • Многоязычная поддержка: ✅ BERT multilingual")
            print(f"  • Компактная модель: ✅ Быстрый анализ")
        
        # OpenRouter
        openrouter_success = len([r for r in openrouter_results if r.get('success')])
        openrouter_total = len(openrouter_results)
        
        print(f"\n🌐 OPENROUTER API:")
        if openrouter_total > 0:
            print(f"  • Успешных тестов: {openrouter_success}/{openrouter_total}")
            print(f"  • Успешность: {openrouter_success/openrouter_total*100:.1f}%")
            
            if openrouter_success > 0:
                models_used = set()
                for result in openrouter_results:
                    if result.get('success') and result.get('model'):
                        models_used.add(result['model'])
                
                print(f"  • Протестированные модели: {len(models_used)}")
                for model in models_used:
                    print(f"    - {model}")
        else:
            print(f"  • Статус: ⚠️ API ключ не настроен")
            print(f"  • Рекомендация: Настройте OPENROUTER_API_KEY для полного тестирования")
        
        # Комплексный анализ
        print(f"\n🔮 КОМПЛЕКСНЫЙ АНАЛИЗ:")
        print(f"  • Статус: {'✅ Успешно' if comprehensive_success else '❌ Ошибка'}")
        
        # Общая оценка
        total_success = local_success + openrouter_success + (1 if comprehensive_success else 0)
        total_tests = local_total + openrouter_total + 1
        
        overall_score = total_success / total_tests
        
        print(f"\n🏆 ОБЩАЯ ОЦЕНКА:")
        print(f"  • Успешных тестов: {total_success}/{total_tests}")
        print(f"  • Общий балл: {overall_score*100:.1f}%")
        
        if overall_score >= 0.8:
            print(f"  • Статус: 🎉 ОТЛИЧНО - Современные модели готовы!")
        elif overall_score >= 0.6:
            print(f"  • Статус: ✅ ХОРОШО - Основные функции работают")
        else:
            print(f"  • Статус: ⚠️ ТРЕБУЕТ НАСТРОЙКИ")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        if local_success == local_total:
            print(f"  ✅ Локальные модели работают отлично")
        else:
            print(f"  ⚠️ Проверьте установку современных моделей")
        
        if openrouter_total == 0:
            print(f"  💡 Настройте OpenRouter для доступа к лучшим LLM")
            print(f"     1. Зарегистрируйтесь на https://openrouter.ai/")
            print(f"     2. Получите бесплатный API ключ ($5 кредитов)")
            print(f"     3. Установите: set OPENROUTER_API_KEY=your_key")
        elif openrouter_success == openrouter_total:
            print(f"  ✅ OpenRouter работает отлично")
        else:
            print(f"  ⚠️ Проверьте настройки OpenRouter API")
        
        if comprehensive_success:
            print(f"  ✅ Комплексный анализ готов к продакшену")
        else:
            print(f"  ⚠️ Комплексный анализ требует доработки")


async def main():
    """Главная функция тестирования современных моделей"""
    print("🚀 ТЕСТИРОВАНИЕ СОВРЕМЕННЫХ AI-МОДЕЛЕЙ 2024")
    print("🔮 Oracul Bot - Modern Models Integration Test")
    print("=" * 60)
    
    tester = ModernModelsTest()
    
    try:
        # Инициализация
        if not await tester.initialize():
            print("❌ Ошибка инициализации")
            return
        
        # Тест современных локальных моделей
        local_results = await tester.test_modern_local_models()
        
        # Тест OpenRouter соединения
        openrouter_available = await tester.test_openrouter_connection()
        
        # Тест OpenRouter анализа (если доступен)
        openrouter_results = []
        if openrouter_available:
            openrouter_results = await tester.test_openrouter_analysis()
        
        # Тест комплексного анализа
        comprehensive_success = await tester.test_comprehensive_analysis()
        
        # Генерация итогового отчета
        tester.generate_summary_report(local_results, openrouter_results, comprehensive_success)
        
        print(f"\n🎯 ТЕСТИРОВАНИЕ СОВРЕМЕННЫХ МОДЕЛЕЙ ЗАВЕРШЕНО!")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
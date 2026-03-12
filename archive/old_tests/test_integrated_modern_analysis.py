#!/usr/bin/env python3
"""
Тест интегрированного анализа с современными моделями
Проверяет работу локальных + OpenRouter моделей вместе
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

from analyzers.local_text_analyzer import LocalTextAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedAnalysisTest:
    """Тест интегрированного анализа"""
    
    def __init__(self):
        self.analyzer = None
    
    async def initialize(self):
        """Инициализация анализатора"""
        try:
            print("🚀 Инициализация интегрированного анализатора...")
            
            # Проверяем настройки
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            if openrouter_key:
                print(f"🔑 OpenRouter API ключ: {openrouter_key[:20]}...")
            else:
                print("⚠️ OpenRouter API ключ не найден")
            
            # Инициализируем анализатор
            self.analyzer = LocalTextAnalyzer()
            
            print("✅ Инициализация завершена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def test_local_only_analysis(self):
        """Тест только локальных моделей"""
        print("\n🧠 ТЕСТ ЛОКАЛЬНЫХ МОДЕЛЕЙ")
        print("=" * 50)
        
        test_text = "Сегодня отличный день! Много планов и хорошее настроение. Чувствую себя очень энергично."
        
        print(f"📝 Текст: {test_text}")
        
        try:
            # Анализ без современных моделей
            result = await self.analyzer.analyze(test_text, use_modern=False)
            
            if result.get('success'):
                print("✅ Локальный анализ успешен")
                
                # Показываем результаты
                sentiment = result.get('sentiment', {})
                if sentiment:
                    print(f"📊 Тональность: {sentiment.get('label')} ({sentiment.get('confidence', 0)*100:.1f}%)")
                
                emotions = result.get('emotions', {})
                if emotions:
                    top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
                    emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions if s > 0.1])
                    if emotion_str:
                        print(f"😊 Эмоции: {emotion_str}")
                
                personality = result.get('personality', {})
                if personality:
                    top_traits = sorted(personality.items(), key=lambda x: x[1], reverse=True)[:2]
                    trait_str = ', '.join([f"{t}: {s*100:.1f}%" for t, s in top_traits if s > 0.3])
                    if trait_str:
                        print(f"👤 Личность: {trait_str}")
                
                methods = result.get('analysis_methods', [])
                print(f"🔧 Методы: {', '.join(methods)}")
                
                return True
            else:
                print(f"❌ Ошибка локального анализа: {result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return False
    
    async def test_integrated_analysis(self):
        """Тест интегрированного анализа (локальные + современные)"""
        print("\n🔮 ТЕСТ ИНТЕГРИРОВАННОГО АНАЛИЗА")
        print("=" * 50)
        
        test_text = "Работа над проектом идет хорошо, но есть некоторые сложности. Команда старается, хотя иногда возникают разногласия. В целом настроен оптимистично, но беспокоюсь о дедлайнах."
        
        print(f"📝 Текст: {test_text}")
        
        try:
            # Анализ с современными моделями
            result = await self.analyzer.analyze(test_text, use_modern=True)
            
            if result.get('success'):
                print("✅ Интегрированный анализ успешен")
                
                # Локальные результаты
                print("\n🧠 ЛОКАЛЬНЫЕ МОДЕЛИ:")
                sentiment = result.get('sentiment', {})
                if sentiment:
                    print(f"  📊 Тональность: {sentiment.get('label')} ({sentiment.get('confidence', 0)*100:.1f}%)")
                
                emotions = result.get('emotions', {})
                if emotions:
                    top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
                    emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions if s > 0.1])
                    if emotion_str:
                        print(f"  😊 Эмоции: {emotion_str}")
                
                # Современные результаты
                modern_analysis = result.get('modern_analysis', {})
                if modern_analysis and modern_analysis.get('success'):
                    print("\n🤖 СОВРЕМЕННЫЕ МОДЕЛИ (OpenRouter):")
                    print(f"  🔧 Модель: {modern_analysis.get('model_used')}")
                    
                    openrouter_data = modern_analysis.get('openrouter_analysis', {})
                    
                    if 'sentiment' in openrouter_data:
                        or_sent = openrouter_data['sentiment']
                        print(f"  📊 Тональность: {or_sent.get('label')} ({or_sent.get('confidence', 0)*100:.1f}%)")
                    
                    if 'emotions' in openrouter_data:
                        or_emotions = openrouter_data['emotions']
                        if isinstance(or_emotions, dict):
                            top_or_emotions = sorted(or_emotions.items(), key=lambda x: x[1], reverse=True)[:2]
                            or_emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_or_emotions if s > 0.1])
                            if or_emotion_str:
                                print(f"  😊 Эмоции: {or_emotion_str}")
                    
                    if 'insights' in openrouter_data:
                        insights = openrouter_data['insights']
                        if isinstance(insights, list) and insights:
                            print(f"  💡 Инсайты: {'; '.join(insights[:2])}")
                    
                    if 'themes' in openrouter_data:
                        themes = openrouter_data['themes']
                        if isinstance(themes, list) and themes:
                            print(f"  🎯 Темы: {', '.join(themes[:3])}")
                
                # Методы анализа
                methods = result.get('analysis_methods', [])
                print(f"\n🔧 Использованные методы: {', '.join(methods)}")
                
                # Рекомендации
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"💡 Рекомендации: {'; '.join(recommendations[:2])}")
                
                return True
            else:
                print(f"❌ Ошибка интегрированного анализа: {result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return False
    
    async def test_comparison_analysis(self):
        """Сравнительный тест локальных vs современных моделей"""
        print("\n⚖️ СРАВНИТЕЛЬНЫЙ АНАЛИЗ")
        print("=" * 50)
        
        test_cases = [
            {
                'name': 'Позитивный текст',
                'text': 'Я очень рад этой новости! Это потрясающе! Наконец-то все получилось.'
            },
            {
                'name': 'Негативный текст',
                'text': 'Мне очень грустно и одиноко. Ничего не получается, все идет не так.'
            },
            {
                'name': 'Нейтральный текст',
                'text': 'Сегодня обычный рабочий день. Выполняю свои задачи по плану.'
            }
        ]
        
        comparison_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Тест {i}: {test_case['name']} ---")
            print(f"📝 Текст: {test_case['text']}")
            
            try:
                # Локальный анализ
                local_result = await self.analyzer.analyze(test_case['text'], use_modern=False)
                
                # Интегрированный анализ
                integrated_result = await self.analyzer.analyze(test_case['text'], use_modern=True)
                
                # Сравниваем результаты
                comparison = {
                    'test_name': test_case['name'],
                    'local_success': local_result.get('success', False),
                    'integrated_success': integrated_result.get('success', False),
                    'methods_count': len(integrated_result.get('analysis_methods', [])),
                    'has_modern': 'openrouter_api' in integrated_result.get('analysis_methods', [])
                }
                
                # Сравнение тональности
                local_sentiment = local_result.get('sentiment', {}).get('label', 'unknown')
                
                modern_analysis = integrated_result.get('modern_analysis', {})
                if modern_analysis.get('success'):
                    openrouter_data = modern_analysis.get('openrouter_analysis', {})
                    modern_sentiment = openrouter_data.get('sentiment', {}).get('label', 'unknown')
                else:
                    modern_sentiment = 'unavailable'
                
                comparison['local_sentiment'] = local_sentiment
                comparison['modern_sentiment'] = modern_sentiment
                comparison['sentiment_match'] = local_sentiment == modern_sentiment
                
                print(f"🧠 Локальная тональность: {local_sentiment}")
                print(f"🤖 Современная тональность: {modern_sentiment}")
                print(f"⚖️ Совпадение: {'✅' if comparison['sentiment_match'] else '❌'}")
                print(f"🔧 Методов использовано: {comparison['methods_count']}")
                
                comparison_results.append(comparison)
                
            except Exception as e:
                print(f"❌ Ошибка сравнения: {e}")
                comparison_results.append({
                    'test_name': test_case['name'],
                    'error': str(e)
                })
        
        return comparison_results
    
    def generate_final_report(self, local_success, integrated_success, comparison_results):
        """Генерация финального отчета"""
        print("\n📊 ФИНАЛЬНЫЙ ОТЧЕТ ИНТЕГРАЦИИ")
        print("=" * 60)
        
        # Общие результаты
        print(f"🧠 ЛОКАЛЬНЫЕ МОДЕЛИ:")
        print(f"  • Статус: {'✅ Работают' if local_success else '❌ Ошибка'}")
        
        print(f"\n🔮 ИНТЕГРИРОВАННЫЙ АНАЛИЗ:")
        print(f"  • Статус: {'✅ Работает' if integrated_success else '❌ Ошибка'}")
        
        # Сравнительный анализ
        if comparison_results:
            successful_comparisons = [r for r in comparison_results if not r.get('error')]
            total_comparisons = len(comparison_results)
            
            print(f"\n⚖️ СРАВНИТЕЛЬНЫЙ АНАЛИЗ:")
            print(f"  • Успешных тестов: {len(successful_comparisons)}/{total_comparisons}")
            
            if successful_comparisons:
                # Анализ совпадений тональности
                sentiment_matches = [r for r in successful_comparisons if r.get('sentiment_match')]
                match_rate = len(sentiment_matches) / len(successful_comparisons) * 100
                
                print(f"  • Совпадение тональности: {len(sentiment_matches)}/{len(successful_comparisons)} ({match_rate:.1f}%)")
                
                # Анализ методов
                modern_available = [r for r in successful_comparisons if r.get('has_modern')]
                modern_rate = len(modern_available) / len(successful_comparisons) * 100
                
                print(f"  • Современные модели доступны: {len(modern_available)}/{len(successful_comparisons)} ({modern_rate:.1f}%)")
                
                # Детали по тестам
                print(f"\n📋 ДЕТАЛИ ТЕСТОВ:")
                for result in successful_comparisons:
                    name = result.get('test_name', 'Unknown')
                    local_sent = result.get('local_sentiment', 'N/A')
                    modern_sent = result.get('modern_sentiment', 'N/A')
                    match = '✅' if result.get('sentiment_match') else '❌'
                    methods = result.get('methods_count', 0)
                    
                    print(f"  • {name}: {local_sent} vs {modern_sent} {match} ({methods} методов)")
        
        # Общая оценка
        total_success = sum([
            1 if local_success else 0,
            1 if integrated_success else 0,
            len([r for r in comparison_results if not r.get('error')])
        ])
        total_tests = 2 + len(comparison_results)
        
        overall_score = total_success / total_tests * 100
        
        print(f"\n🏆 ОБЩАЯ ОЦЕНКА:")
        print(f"  • Успешных компонентов: {total_success}/{total_tests}")
        print(f"  • Общий балл: {overall_score:.1f}%")
        
        if overall_score >= 80:
            print(f"  • Статус: 🎉 ОТЛИЧНО - Интеграция полностью готова!")
        elif overall_score >= 60:
            print(f"  • Статус: ✅ ХОРОШО - Основные функции работают")
        else:
            print(f"  • Статус: ⚠️ ТРЕБУЕТ ДОРАБОТКИ")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        if local_success and integrated_success:
            print(f"  ✅ Система готова к продакшену")
            print(f"  🚀 Можно интегрировать в основной Oracul Bot")
        elif integrated_success:
            print(f"  ⚡ Интегрированный анализ работает, локальные модели опциональны")
        else:
            print(f"  ⚠️ Требуется дополнительная настройка")
        
        if any(r.get('has_modern') for r in comparison_results if not r.get('error')):
            print(f"  🤖 OpenRouter модели успешно интегрированы")
        else:
            print(f"  ❌ Проверьте настройки OpenRouter API")


async def main():
    """Главная функция тестирования интегрированного анализа"""
    print("🚀 ТЕСТИРОВАНИЕ ИНТЕГРИРОВАННОГО АНАЛИЗА")
    print("🔮 Oracul Bot - Local + Modern Models Integration")
    print("=" * 70)
    
    tester = IntegratedAnalysisTest()
    
    try:
        # Инициализация
        if not await tester.initialize():
            print("❌ Ошибка инициализации")
            return
        
        # Тест локальных моделей
        local_success = await tester.test_local_only_analysis()
        
        # Тест интегрированного анализа
        integrated_success = await tester.test_integrated_analysis()
        
        # Сравнительный анализ
        comparison_results = await tester.test_comparison_analysis()
        
        # Финальный отчет
        tester.generate_final_report(local_success, integrated_success, comparison_results)
        
        print(f"\n🎯 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ЗАВЕРШЕНО!")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
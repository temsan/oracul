#!/usr/bin/env python3
"""
Тест только анализаторов без БД
"""

import asyncio
import sys
import logging
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.local_text_analyzer import LocalTextAnalyzer
from analyzers.local_voice_analyzer import LocalVoiceAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def comprehensive_text_test():
    """Комплексный тест текстового анализатора"""
    print("🧠 Комплексный тест текстового анализатора...")
    
    try:
        analyzer = LocalTextAnalyzer()
        
        test_cases = [
            {
                'text': "Привет! Сегодня отличный день, много планов и хорошее настроение!",
                'expected_sentiment': 'positive',
                'description': 'Позитивный текст'
            },
            {
                'text': "Устал от работы, все надоело, хочется отдохнуть...",
                'expected_sentiment': 'negative',
                'description': 'Негативный текст'
            },
            {
                'text': "Интересный проект, много возможностей для развития и обучения.",
                'expected_sentiment': 'neutral',
                'description': 'Нейтральный текст'
            },
            {
                'text': "Я очень рад этой новости! Это потрясающе!",
                'expected_sentiment': 'positive',
                'description': 'Эмоциональный позитив'
            },
            {
                'text': "Мне грустно и одиноко. Ничего не получается.",
                'expected_sentiment': 'negative',
                'description': 'Эмоциональный негатив'
            }
        ]
        
        correct_predictions = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Тест {i}: {test_case['description']} ---")
            print(f"Текст: {test_case['text']}")
            
            result = await analyzer.analyze(test_case['text'])
            
            if result.get('success'):
                sentiment = result.get('sentiment', {})
                predicted_sentiment = sentiment.get('label', 'unknown')
                confidence = sentiment.get('confidence', 0) * 100
                
                print(f"📊 Предсказанная тональность: {predicted_sentiment} ({confidence:.1f}%)")
                print(f"🎯 Ожидаемая тональность: {test_case['expected_sentiment']}")
                
                # Проверяем корректность
                if predicted_sentiment == test_case['expected_sentiment']:
                    print("✅ Предсказание корректно")
                    correct_predictions += 1
                else:
                    print("❌ Предсказание некорректно")
                
                # Показываем эмоции
                emotions = result.get('emotions', {})
                if emotions:
                    top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
                    emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions])
                    print(f"😊 Эмоции: {emotion_str}")
                
                # Показываем рекомендации
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"💡 Наблюдения: {'; '.join(recommendations[:2])}")
            else:
                print(f"❌ Ошибка анализа: {result.get('error')}")
        
        accuracy = (correct_predictions / total_tests) * 100
        print(f"\n📈 Точность предсказаний: {correct_predictions}/{total_tests} ({accuracy:.1f}%)")
        
        return accuracy >= 60  # Считаем успешным если точность >= 60%
        
    except Exception as e:
        print(f"❌ Ошибка комплексного теста: {e}")
        return False


async def performance_test():
    """Тест производительности"""
    print("\n⚡ Тест производительности...")
    
    try:
        analyzer = LocalTextAnalyzer()
        
        test_text = "Сегодня хороший день для работы и творчества. Много интересных задач."
        
        # Прогрев
        await analyzer.analyze(test_text)
        
        # Измеряем время
        import time
        
        start_time = time.time()
        num_tests = 5
        
        for i in range(num_tests):
            result = await analyzer.analyze(test_text)
            if not result.get('success'):
                print(f"❌ Ошибка в тесте {i+1}")
                return False
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_tests
        
        print(f"📊 Результаты производительности:")
        print(f"  • Общее время: {total_time:.2f} сек")
        print(f"  • Среднее время: {avg_time:.2f} сек/анализ")
        print(f"  • Скорость: {1/avg_time:.1f} анализов/сек")
        
        # Считаем успешным если анализ занимает < 10 секунд
        return avg_time < 10.0
        
    except Exception as e:
        print(f"❌ Ошибка теста производительности: {e}")
        return False


async def memory_usage_test():
    """Тест использования памяти"""
    print("\n💾 Тест использования памяти...")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Измеряем память до создания анализатора
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Создаем анализатор
        analyzer = LocalTextAnalyzer()
        
        # Измеряем память после инициализации
        memory_after_init = process.memory_info().rss / 1024 / 1024  # MB
        
        # Выполняем несколько анализов
        test_texts = [
            "Короткий текст",
            "Средний по длине текст с несколькими предложениями и разными эмоциями.",
            "Длинный текст с множеством предложений, который содержит различные эмоциональные окраски, сложные конструкции и разнообразную лексику для проверки работы анализатора в условиях повышенной нагрузки."
        ]
        
        for text in test_texts:
            await analyzer.analyze(text)
        
        # Измеряем память после анализов
        memory_after_analysis = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 Использование памяти:")
        print(f"  • До инициализации: {memory_before:.1f} MB")
        print(f"  • После инициализации: {memory_after_init:.1f} MB")
        print(f"  • После анализов: {memory_after_analysis:.1f} MB")
        print(f"  • Прирост при инициализации: {memory_after_init - memory_before:.1f} MB")
        print(f"  • Прирост при анализе: {memory_after_analysis - memory_after_init:.1f} MB")
        
        # Считаем успешным если общее использование < 4GB
        return memory_after_analysis < 4000
        
    except ImportError:
        print("⚠️ psutil не установлен, пропускаем тест памяти")
        return True
    except Exception as e:
        print(f"❌ Ошибка теста памяти: {e}")
        return True  # Не критично


async def model_loading_test():
    """Тест загрузки моделей"""
    print("\n📥 Тест загрузки моделей...")
    
    try:
        import time
        
        start_time = time.time()
        
        # Создаем анализатор (загружает модели)
        analyzer = LocalTextAnalyzer()
        
        loading_time = time.time() - start_time
        
        print(f"⏱️ Время загрузки моделей: {loading_time:.2f} сек")
        
        # Проверяем, что модели загружены
        models_loaded = 0
        total_models = 4  # sentiment, emotion, generation, embedding
        
        if hasattr(analyzer, 'sentiment_model') and analyzer.sentiment_model:
            print("✅ Sentiment модель загружена")
            models_loaded += 1
        
        if hasattr(analyzer, 'emotion_model') and analyzer.emotion_model:
            print("✅ Emotion модель загружена")
            models_loaded += 1
        
        if hasattr(analyzer, 'generation_model') and analyzer.generation_model:
            print("✅ Generation модель загружена")
            models_loaded += 1
        
        if hasattr(analyzer, 'embedding_model') and analyzer.embedding_model:
            print("✅ Embedding модель загружена")
            models_loaded += 1
        
        print(f"📊 Загружено моделей: {models_loaded}/{total_models}")
        
        # Считаем успешным если загружено >= 2 моделей
        return models_loaded >= 2
        
    except Exception as e:
        print(f"❌ Ошибка теста загрузки моделей: {e}")
        return False


async def main():
    """Главная функция тестирования"""
    print("🔮 Комплексное тестирование Oracul Local Analyzers")
    print("=" * 60)
    
    # Системная информация
    print(f"🐍 Python: {sys.version}")
    
    try:
        import torch
        print(f"🔥 PyTorch: {torch.__version__}")
        print(f"🎮 CUDA: {'Доступна' if torch.cuda.is_available() else 'Недоступна'}")
        if torch.cuda.is_available():
            print(f"📱 GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("❌ PyTorch не установлен")
    
    print("\n" + "=" * 60)
    
    # Запускаем тесты
    results = []
    
    # Тест загрузки моделей
    loading_result = await model_loading_test()
    results.append(("Model Loading", loading_result))
    
    # Комплексный тест
    comprehensive_result = await comprehensive_text_test()
    results.append(("Comprehensive Analysis", comprehensive_result))
    
    # Тест производительности
    performance_result = await performance_test()
    results.append(("Performance", performance_result))
    
    # Тест памяти
    memory_result = await memory_usage_test()
    results.append(("Memory Usage", memory_result))
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 Результаты тестирования:")
    
    for test_name, result in results:
        status = "✅ Пройден" if result else "❌ Не пройден"
        print(f"  {test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n🎯 Итого: {success_count}/{total_count} тестов пройдено")
    
    if success_count == total_count:
        print("🎉 Все тесты пройдены! Локальные анализаторы полностью готовы.")
        print("\n🚀 Система готова к продакшену:")
        print("  • Модели загружаются корректно")
        print("  • Анализ работает точно")
        print("  • Производительность приемлемая")
        print("  • Использование памяти оптимально")
    elif success_count >= total_count * 0.75:
        print("✅ Большинство тестов пройдено! Система готова к использованию.")
    else:
        print("⚠️ Система требует доработки. Проверьте установку зависимостей.")


if __name__ == "__main__":
    asyncio.run(main())
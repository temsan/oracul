#!/usr/bin/env python3
"""
Тест локальных моделей Oracul Bot
"""

import asyncio
import sys
import logging
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.local_text_analyzer import LocalTextAnalyzer
from services.vllm_service import vllm_service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_text_analyzer():
    """Тест локального анализатора текста"""
    print("🧠 Тестирование локального анализатора текста...")
    
    try:
        analyzer = LocalTextAnalyzer()
        
        # Тестовые тексты
        test_texts = [
            "Привет! Сегодня отличный день, много планов и хорошее настроение!",
            "Устал от работы, все надоело, хочется отдохнуть...",
            "Интересный проект, много возможностей для развития и обучения."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n--- Тест {i} ---")
            print(f"Текст: {text}")
            
            result = await analyzer.analyze(text)
            
            if result.get('success'):
                print("✅ Анализ успешен")
                
                # Тональность
                sentiment = result.get('sentiment', {})
                if sentiment:
                    print(f"📊 Тональность: {sentiment.get('label', 'unknown')} ({sentiment.get('confidence', 0)*100:.1f}%)")
                
                # Эмоции
                emotions = result.get('emotions', {})
                if emotions:
                    top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"😊 Эмоции: {', '.join([f'{e}: {s*100:.1f}%' for e, s in top_emotions])}")
                
                # Личность
                personality = result.get('personality', {})
                if personality:
                    top_traits = sorted(personality.items(), key=lambda x: x[1], reverse=True)[:2]
                    print(f"👤 Личность: {', '.join([f'{t}: {s*100:.1f}%' for t, s in top_traits])}")
                
                # Рекомендации
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"💡 Наблюдения: {'; '.join(recommendations[:2])}")
            else:
                print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
        
        print("\n✅ Тест анализатора текста завершен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования анализатора текста: {e}")
        return False


async def test_vllm_service():
    """Тест vLLM сервиса"""
    print("\n⚡ Тестирование vLLM сервиса...")
    
    try:
        # Проверяем доступность
        is_available = await vllm_service.health_check()
        
        if is_available:
            print("✅ vLLM сервер доступен")
            
            # Получаем модели
            models = await vllm_service.get_models()
            print(f"📋 Доступные модели: {len(models)}")
            for model in models[:3]:  # Показываем первые 3
                print(f"  • {model}")
            
            # Тестируем генерацию
            test_prompt = "Анализ текста показывает"
            result = await vllm_service.generate(
                prompt=test_prompt,
                max_tokens=50,
                temperature=0.7
            )
            
            if result.get('success'):
                print(f"✅ Генерация работает: '{result['text'][:100]}...'")
            else:
                print(f"❌ Ошибка генерации: {result.get('error')}")
            
        else:
            print("⚠️ vLLM сервер недоступен")
            print("💡 Для запуска: python -m vllm.entrypoints.api_server --model microsoft/DialoGPT-medium")
        
        return is_available
        
    except Exception as e:
        print(f"❌ Ошибка тестирования vLLM: {e}")
        return False


async def test_model_loading():
    """Тест загрузки моделей"""
    print("\n📥 Тестирование загрузки моделей...")
    
    try:
        # Тест Whisper
        print("🎤 Загрузка Whisper...")
        import whisper
        model = whisper.load_model("base")
        print("✅ Whisper base загружен")
        
        # Тест Transformers
        print("🧠 Загрузка Transformers...")
        from transformers import pipeline
        
        # Sentiment model
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="blanchefort/rubert-base-cased-sentiment",
            device=0 if analyzer.device == "cuda" else -1
        )
        print("✅ RuBERT sentiment загружен")
        
        # Emotion model
        emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=0 if analyzer.device == "cuda" else -1
        )
        print("✅ DistilRoBERTa emotion загружен")
        
        print("✅ Все модели успешно загружены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки моделей: {e}")
        return False


async def main():
    """Главная функция тестирования"""
    print("🔮 Тестирование Oracul Bot Local Models")
    print("=" * 50)
    
    # Проверяем системные требования
    print(f"🐍 Python: {sys.version}")
    
    try:
        import torch
        print(f"🔥 PyTorch: {torch.__version__}")
        print(f"🎮 CUDA: {'Доступна' if torch.cuda.is_available() else 'Недоступна'}")
        if torch.cuda.is_available():
            print(f"📱 GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("❌ PyTorch не установлен")
    
    print("\n" + "=" * 50)
    
    # Запускаем тесты
    results = []
    
    # Тест анализатора текста
    text_result = await test_text_analyzer()
    results.append(("Text Analyzer", text_result))
    
    # Тест vLLM
    vllm_result = await test_vllm_service()
    results.append(("vLLM Service", vllm_result))
    
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
    elif success_count > 0:
        print("⚠️ Система частично готова. Некоторые функции могут быть ограничены.")
    else:
        print("❌ Система не готова. Проверьте установку зависимостей.")


if __name__ == "__main__":
    asyncio.run(main())
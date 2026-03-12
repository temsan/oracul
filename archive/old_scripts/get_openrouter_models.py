#!/usr/bin/env python3
"""
Получение списка бесплатных моделей OpenRouter с метриками throughput и latency
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import json

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
BASE_URL = "https://openrouter.ai/api/v1"


async def get_free_models():
    """Получить список бесплатных моделей с метриками"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://oracul-bot.local",
            "X-Title": "Oracul Bot"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    models = data.get('data', [])
                    
                    # Фильтруем только бесплатные модели
                    free_models = []
                    for model in models:
                        pricing = model.get('pricing', {})
                        prompt_price = float(pricing.get('prompt', '1'))
                        completion_price = float(pricing.get('completion', '1'))
                        
                        if prompt_price == 0 and completion_price == 0:
                            free_models.append({
                                'id': model.get('id'),
                                'name': model.get('name'),
                                'context_length': model.get('context_length', 0),
                                'top_provider': model.get('top_provider', {}),
                                'architecture': model.get('architecture', {})
                            })
                    
                    return free_models
                else:
                    print(f"❌ Ошибка API: {response.status}")
                    error_text = await response.text()
                    print(f"Ответ: {error_text}")
                    return []
                    
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return []


async def analyze_models():
    """Анализ моделей по throughput и latency"""
    print("🔍 ПОЛУЧЕНИЕ ДАННЫХ О БЕСПЛАТНЫХ МОДЕЛЯХ OPENROUTER")
    print("=" * 70)
    
    models = await get_free_models()
    
    if not models:
        print("❌ Не удалось получить список моделей")
        return
    
    print(f"✅ Найдено {len(models)} бесплатных моделей\n")
    
    # Анализируем метрики
    models_with_metrics = []
    
    for model in models:
        model_id = model['id']
        top_provider = model.get('top_provider', {})
        
        # Извлекаем метрики
        max_completion_tokens = top_provider.get('max_completion_tokens')
        is_moderated = top_provider.get('is_moderated', False)
        
        models_with_metrics.append({
            'id': model_id,
            'name': model['name'],
            'context_length': model['context_length'],
            'max_completion_tokens': max_completion_tokens,
            'is_moderated': is_moderated
        })
    
    # Сортируем по контексту (косвенный показатель возможностей)
    models_by_context = sorted(models_with_metrics, key=lambda x: x['context_length'], reverse=True)
    
    print("📊 ТОП-10 МОДЕЛЕЙ ПО РАЗМЕРУ КОНТЕКСТА:")
    print("-" * 70)
    for i, model in enumerate(models_by_context[:10], 1):
        print(f"{i}. {model['id']}")
        print(f"   Контекст: {model['context_length']:,} токенов")
        print(f"   Max completion: {model['max_completion_tokens']}")
        print()
    
    # Рекомендуемые модели на основе известных характеристик
    print("\n🎯 РЕКОМЕНДУЕМЫЕ МОДЕЛИ (баланс throughput/latency):")
    print("-" * 70)
    
    recommended = [
        "openai/gpt-oss-120b:free",
        "openai/gpt-oss-20b:free", 
        "meta-llama/llama-3.2-3b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "qwen/qwen-2-7b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-2-2b-it:free"
    ]
    
    print("\nПриоритет по throughput (высокая пропускная способность):")
    throughput_priority = [
        "meta-llama/llama-3.2-3b-instruct:free",  # 3B - быстрая
        "google/gemma-2-2b-it:free",  # 2B - очень быстрая
        "qwen/qwen-2-7b-instruct:free",  # 7B - хороший баланс
        "mistralai/mistral-7b-instruct:free"  # 7B - стабильная
    ]
    
    for i, model_id in enumerate(throughput_priority, 1):
        model_data = next((m for m in models_with_metrics if m['id'] == model_id), None)
        if model_data:
            print(f"{i}. {model_id}")
            print(f"   Контекст: {model_data['context_length']:,} токенов")
    
    print("\nПриоритет по latency (низкая задержка):")
    latency_priority = [
        "meta-llama/llama-3.2-3b-instruct:free",  # Самая быстрая
        "google/gemma-2-2b-it:free",  # Очень низкая latency
        "microsoft/phi-3-mini-128k-instruct:free",  # Оптимизированная
        "qwen/qwen-2-7b-instruct:free"  # Хорошая скорость
    ]
    
    for i, model_id in enumerate(latency_priority, 1):
        model_data = next((m for m in models_with_metrics if m['id'] == model_id), None)
        if model_data:
            print(f"{i}. {model_id}")
            print(f"   Контекст: {model_data['context_length']:,} токенов")
    
    print("\n🏆 ФИНАЛЬНАЯ РЕКОМЕНДАЦИЯ (топ-4 по приоритету):")
    print("-" * 70)
    final_recommendation = [
        ("openai/gpt-oss-120b:free", "Лучшее качество (120B), может быть rate limit"),
        ("openai/gpt-oss-20b:free", "Хорошее качество (20B), может быть rate limit"),
        ("meta-llama/llama-3.2-3b-instruct:free", "Лучший баланс throughput/latency (3B)"),
        ("microsoft/phi-3-mini-128k-instruct:free", "Большой контекст (128k) + хорошая скорость")
    ]
    
    for i, (model_id, description) in enumerate(final_recommendation, 1):
        model_data = next((m for m in models_with_metrics if m['id'] == model_id), None)
        print(f"\n{i}. {model_id}")
        print(f"   {description}")
        if model_data:
            print(f"   Контекст: {model_data['context_length']:,} токенов")
    
    # Сохраняем полный список в файл
    with open('openrouter_free_models.json', 'w', encoding='utf-8') as f:
        json.dump(models_with_metrics, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Полный список сохранен в openrouter_free_models.json")


async def main():
    await analyze_models()


if __name__ == "__main__":
    asyncio.run(main())

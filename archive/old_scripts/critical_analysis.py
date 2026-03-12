#!/usr/bin/env python3
"""
Критический анализ архитектуры RuKallama с использованием LLM
"""

import os
import json
import asyncio
from datetime import datetime
import openai

# Настройки
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'openai/gpt-4o-mini')

async def critical_llm_analysis():
    """Критический анализ архитектуры RuKallama через LLM"""
    
    print("🔍 Запуск критического анализа архитектуры RuKallama...")
    
    # Инициализация OpenAI клиента для OpenRouter
    client = openai.AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )
    
    # Данные о RuKallama из анализа канала
    rukallama_data = """
    АРХИТЕКТУРА RUKALLAMA (SplineGPT):
    
    Основные компоненты:
    - KAN (Kolmogorov-Arnold Networks) в Q/K проекциях attention (НЕ в MLP)
    - MoE (Mixture of Experts) каждый 3-й блок
    - RoPE позиционное кодирование
    - Маскинг диалогов - loss только по ответам
    
    Обучающие данные:
    - Претрейн: 763 советские книги (1950-1990х), физика, химия, математика, БСЭ
    - 16 эпох, Loss 1.8, плато достигнуто
    - Собственная токенизация с ёфикацией (379K словарь)
    - Файнтюн: 3052 JSON (4 типа), Saiga Scored 41K диалогов, OpenAssistant oasst2
    
    Технические параметры:
    - A100 80GB
    - LR: 6e-5 (в 10 раз меньше претрейна)
    - Batch: 64, effective 256
    - Replay buffer 15%
    
    Заявления автора:
    - "Единственная в мире модель, где на KAN заменено абсолютно всё"
    - Цель: "надаёт за щеку GPT-3 Turbo"
    - 10 месяцев разработки
    - Претрейн с нуля на русском языке
    """
    
    # Промпт для критического анализа
    analysis_prompt = f"""
    Ты эксперт по архитектурам нейронных сетей и языковых моделей. Проведи КРИТИЧЕСКИЙ анализ архитектуры RuKallama.

    Данные о модели:
    {rukallama_data}

    Проанализируй следующие аспекты:

    1. АРХИТЕКТУРНЫЕ РЕШЕНИЯ:
    - Обоснованность использования KAN в Q/K проекциях вместо MLP
    - Эффективность MoE каждый 3-й блок
    - Совместимость KAN + MoE + RoPE

    2. ОБУЧАЮЩИЕ ДАННЫЕ:
    - Качество и релевантность советских книг 1950-1990х для современной модели
    - Достаточность 763 книг для претрейна
    - Проблемы с устаревшими данными

    3. ТЕХНИЧЕСКИЕ АСПЕКТЫ:
    - Loss 1.8 - хороший ли это результат?
    - Размер словаря 379K - оптимален ли?
    - Параметры обучения

    4. ЗАЯВЛЕНИЯ И РЕАЛЬНОСТЬ:
    - Реалистичность цели "обогнать GPT-3 Turbo"
    - Уникальность "единственной KAN модели в мире"
    - Потенциальные проблемы и ограничения

    5. СРАВНЕНИЕ С МЕЙНСТРИМОМ:
    - Преимущества и недостатки по сравнению с Transformer архитектурой
    - Масштабируемость решения
    - Практическая применимость

    Будь объективен, указывай как сильные стороны, так и потенциальные проблемы.
    Оцени вероятность успеха проекта по шкале 1-10 с обоснованием.
    """
    
    try:
        print("🤖 Отправка запроса к LLM для анализа...")
        
        response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "Ты эксперт по архитектурам нейронных сетей, машинному обучению и языковым моделям. Твоя задача - дать объективный критический анализ, основанный на современных знаниях в области ML/AI."
                },
                {
                    "role": "user", 
                    "content": analysis_prompt
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        analysis_result = response.choices[0].message.content
        
        print("\n" + "="*80)
        print("🧠 КРИТИЧЕСКИЙ АНАЛИЗ АРХИТЕКТУРЫ RUKALLAMA")
        print("="*80)
        print(analysis_result)
        
        # Дополнительный анализ конкретных технических аспектов
        technical_prompt = """
        Дай более детальный технический анализ следующих аспектов RuKallama:

        1. KAN в Q/K проекциях attention:
        - Теоретическое обоснование
        - Вычислительная сложность vs традиционные linear layers
        - Потенциальные проблемы с градиентами

        2. Комбинация KAN + MoE:
        - Совместимость архитектур
        - Влияние на обучение и инференс
        - Возможные конфликты

        3. Данные 1950-1990х:
        - Влияние на современность знаний
        - Проблемы с терминологией и концепциями
        - Bias в сторону советской научной школы

        4. Размер модели и ресурсы:
        - Оценка количества параметров
        - Эффективность использования A100 80GB
        - Сравнение с современными моделями

        Будь максимально техничен и конкретен.
        """
        
        print("\n🔬 Запрос детального технического анализа...")
        
        technical_response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "Ты эксперт по техническим деталям архитектур нейронных сетей. Фокусируйся на математических и вычислительных аспектах."
                },
                {
                    "role": "user", 
                    "content": technical_prompt
                }
            ],
            max_tokens=1500,
            temperature=0.2
        )
        
        technical_analysis = technical_response.choices[0].message.content
        
        print("\n" + "="*80)
        print("⚙️ ДЕТАЛЬНЫЙ ТЕХНИЧЕСКИЙ АНАЛИЗ")
        print("="*80)
        print(technical_analysis)
        
        # Прогноз и рекомендации
        prediction_prompt = """
        На основе проведенного анализа RuKallama, дай:

        1. ПРОГНОЗ УСПЕХА (1-10 баллов):
        - Техническая реализуемость
        - Конкурентоспособность
        - Практическая применимость

        2. ОСНОВНЫЕ РИСКИ:
        - Технические риски
        - Ресурсные ограничения
        - Рыночные факторы

        3. РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:
        - Архитектурные изменения
        - Данные и обучение
        - Стратегия развития

        4. СРАВНЕНИЕ С АЛЬТЕРНАТИВАМИ:
        - Что лучше делают существующие решения
        - Уникальные преимущества RuKallama
        - Ниши применения

        Будь реалистичен и конструктивен.
        """
        
        print("\n🎯 Запрос прогноза и рекомендаций...")
        
        prediction_response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "Ты стратегический консультант по AI проектам. Твоя задача - дать реалистичный прогноз и практические рекомендации."
                },
                {
                    "role": "user", 
                    "content": prediction_prompt
                }
            ],
            max_tokens=1200,
            temperature=0.4
        )
        
        prediction_analysis = prediction_response.choices[0].message.content
        
        print("\n" + "="*80)
        print("🎯 ПРОГНОЗ И РЕКОМЕНДАЦИИ")
        print("="*80)
        print(prediction_analysis)
        
        # Сохраняем полный анализ
        full_analysis = {
            "general_analysis": analysis_result,
            "technical_analysis": technical_analysis,
            "prediction_and_recommendations": prediction_analysis,
            "analysis_date": datetime.now().isoformat(),
            "model_used": DEFAULT_MODEL,
            "source_data": rukallama_data
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis/rukallama_critical_analysis_{timestamp}.json"
        
        os.makedirs("analysis", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(full_analysis, f, ensure_ascii=False, indent=2)
        
        # Создаем markdown отчет
        markdown_report = f"""# 🔍 Критический анализ архитектуры RuKallama

**Дата анализа:** {datetime.now().strftime("%d.%m.%Y %H:%M")}  
**Модель для анализа:** {DEFAULT_MODEL}

## 🧠 Общий анализ

{analysis_result}

## ⚙️ Технический анализ

{technical_analysis}

## 🎯 Прогноз и рекомендации

{prediction_analysis}

---

*Анализ выполнен с использованием LLM для объективной оценки архитектурных решений*
"""
        
        markdown_filename = f"analysis/rukallama_critical_analysis_{timestamp}.md"
        
        with open(markdown_filename, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        print(f"\n💾 Анализ сохранен:")
        print(f"   JSON: {filename}")
        print(f"   Markdown: {markdown_filename}")
        
        return full_analysis
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Главная функция"""
    print("🔮 КРИТИЧЕСКИЙ АНАЛИЗ RUKALLAMA")
    print("="*50)
    
    if not OPENROUTER_API_KEY:
        print("❌ Не найден OPENROUTER_API_KEY в переменных окружения")
        return
    
    analysis = await critical_llm_analysis()
    
    if analysis:
        print("\n✅ Критический анализ завершен!")
        print("\n🎯 КРАТКИЕ ВЫВОДЫ:")
        print("   • Использован LLM для объективной оценки")
        print("   • Проанализированы архитектурные решения")
        print("   • Оценены риски и перспективы")
        print("   • Даны практические рекомендации")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
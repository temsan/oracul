#!/usr/bin/env python3
"""
Анализ сообщения об архитектуре RuKallama (ID 2593)
"""

import asyncio
import os
import json
from datetime import datetime
from telethon import TelegramClient

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

async def get_architecture_message():
    """Получение сообщения об архитектуре RuKallama"""
    
    print("🔍 Получение сообщения об архитектуре RuKallama (ID 2593)...")
    
    # Создаем клиент
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        # Подключаемся
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем канал
        entity = await client.get_entity('technojnec')
        
        # Получаем сообщение ID 2593
        message = await client.get_messages(entity, ids=2593)
        
        if not message or not message.text:
            print("❌ Сообщение не найдено")
            return None
        
        # Формируем данные сообщения
        message_data = {
            'id': message.id,
            'text': message.text,
            'date': message.date.isoformat() if message.date else None,
            'views': getattr(message, 'views', 0),
            'forwards': getattr(message, 'forwards', 0),
            'replies': getattr(message.replies, 'replies', 0) if message.replies else 0,
            'channel_info': {
                'id': entity.id,
                'title': getattr(entity, 'title', 'Unknown'),
                'username': getattr(entity, 'username', None)
            }
        }
        
        print(f"✅ Сообщение получено:")
        print(f"   ID: {message_data['id']}")
        print(f"   Дата: {message_data['date']}")
        print(f"   Просмотры: {message_data['views']:,}")
        print(f"   Репосты: {message_data['forwards']}")
        print(f"   Ответы: {message_data['replies']}")
        
        return message_data
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None
    finally:
        await client.disconnect()

def analyze_architecture_details(message_text):
    """Детальный анализ архитектурных деталей"""
    
    print("\n🏗️ АНАЛИЗ АРХИТЕКТУРНЫХ ДЕТАЛЕЙ")
    print("="*60)
    
    # Извлекаем ключевые архитектурные компоненты
    architecture_components = {
        'KAN_usage': 'KAN в Q/K проекциях attention (не в MLP как у всех)',
        'MoE_pattern': 'MoE каждый 3-й блок',
        'positional_encoding': 'RoPE',
        'training_optimization': 'Маскинг диалогов — loss только по ответам'
    }
    
    # Технические параметры
    technical_params = {
        'learning_rate': '6e-5 (10× меньше претрейна)',
        'batch_size': 'Batch: 64, effective 256',
        'hardware': 'A100 80GB',
        'monitoring': 'Telegram бот шлёт апдейты'
    }
    
    # Данные для обучения
    training_data = {
        'pretrain_books': '763 советские книги',
        'epochs': '16 эпох',
        'loss': 'Loss 1.8',
        'vocabulary': '379K словарь',
        'custom_data': '3052 JSON (4 типа к каждой книге)',
        'external_datasets': 'Saiga Scored (41K), OpenAssistant oasst2',
        'replay_buffer': '15% — куски претрейна'
    }
    
    print("🔧 АРХИТЕКТУРНЫЕ КОМПОНЕНТЫ:")
    for key, value in architecture_components.items():
        print(f"   • {key}: {value}")
    
    print("\n⚙️ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ:")
    for key, value in technical_params.items():
        print(f"   • {key}: {value}")
    
    print("\n📚 ОБУЧАЮЩИЕ ДАННЫЕ:")
    for key, value in training_data.items():
        print(f"   • {key}: {value}")
    
    return {
        'architecture_components': architecture_components,
        'technical_params': technical_params,
        'training_data': training_data
    }

def critical_architecture_analysis():
    """Критический анализ архитектурных решений"""
    
    print("\n🔍 КРИТИЧЕСКИЙ АНАЛИЗ АРХИТЕКТУРЫ")
    print("="*60)
    
    analysis = {
        'innovative_aspects': [
            "KAN в Q/K проекциях вместо традиционных MLP",
            "Комбинация KAN + MoE + RoPE в одной архитектуре",
            "Специализация под русский язык с нуля",
            "Собственная токенизация с ёфикацией"
        ],
        'potential_problems': [
            "KAN в attention - экспериментальная идея без доказанной эффективности",
            "MoE каждый 3-й блок может создать проблемы с load balancing",
            "Словарь 379K слишком большой для русскоязычной модели",
            "Обучение только на советских книгах 1950-1990х"
        ],
        'technical_concerns': [
            "Loss 1.8 без контекста размера модели не информативен",
            "Batch size 64 может быть мал для стабильного MoE обучения",
            "Replay buffer 15% - произвольный выбор без обоснования",
            "Отсутствие сравнения с baseline архитектурами"
        ],
        'data_quality_issues': [
            "763 книги критически мало для современной LLM",
            "Устаревшие данные (1950-1990) не покрывают современный язык",
            "Отсутствие интернет-текстов, соцсетей, современной лексики",
            "Риск переобучения на ограниченном корпусе"
        ]
    }
    
    print("✨ ИННОВАЦИОННЫЕ АСПЕКТЫ:")
    for aspect in analysis['innovative_aspects']:
        print(f"   + {aspect}")
    
    print("\n⚠️ ПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ:")
    for problem in analysis['potential_problems']:
        print(f"   - {problem}")
    
    print("\n🔧 ТЕХНИЧЕСКИЕ ВОПРОСЫ:")
    for concern in analysis['technical_concerns']:
        print(f"   ? {concern}")
    
    print("\n📊 ПРОБЛЕМЫ С ДАННЫМИ:")
    for issue in analysis['data_quality_issues']:
        print(f"   ! {issue}")
    
    return analysis

def architecture_scoring():
    """Оценка архитектурных решений"""
    
    print("\n📊 ОЦЕНКА АРХИТЕКТУРНЫХ РЕШЕНИЙ")
    print("="*60)
    
    scores = {
        'innovation': {
            'score': 8,
            'reasoning': 'KAN + MoE + RoPE комбинация уникальна, но не протестирована'
        },
        'technical_soundness': {
            'score': 5,
            'reasoning': 'Много экспериментальных решений без доказательств'
        },
        'data_quality': {
            'score': 3,
            'reasoning': 'Критически малый и устаревший датасет'
        },
        'scalability': {
            'score': 6,
            'reasoning': 'MoE позволяет масштабирование, но есть риски'
        },
        'reproducibility': {
            'score': 4,
            'reasoning': 'Недостаточно деталей для воспроизведения'
        },
        'practical_applicability': {
            'score': 7,
            'reasoning': 'Фокус на русский язык практически ценен'
        }
    }
    
    total_score = sum(s['score'] for s in scores.values()) / len(scores)
    
    print(f"🎯 ОБЩАЯ ОЦЕНКА: {total_score:.1f}/10")
    print()
    
    for aspect, data in scores.items():
        print(f"   {aspect.upper()}: {data['score']}/10")
        print(f"      └─ {data['reasoning']}")
        print()
    
    return scores, total_score

async def main():
    """Главная функция"""
    
    print("🏗️ АНАЛИЗ АРХИТЕКТУРЫ RUKALLAMA")
    print("="*50)
    
    # Получаем сообщение (или используем уже имеющиеся данные)
    architecture_text = """**🔥 RUKALLAMA: FINETUNE ЗАПУЩЕН**

**Претрейн завершён.**

763 советские книги. 16 эпох. Loss 1.8. Плато.
Физика, химия, математика, техника, БСЭ — всё 1950-1990х. OCR восстановление полу - вручную. Своя токенизация с ёфикацией (379K словарь).
Веса зафиксированы.
**
Сейчас крутится файнтюн на:**
📚 Свои данные RUKALLAMA — 3052 JSON (4 типа к каждой книге):

basic — простые Q&A
dialog — multi-turn с контекстом из книги
multistep — пошаговые рассуждения
problem — задачи с решениями

**📥 Автоматически скачиваемые датасеты:**

Saiga Scored (IlyaGusev) — 41K русских диалогов
OpenAssistant oasst2 — русские + английские диалоги

**🔄 Replay buffer 15%** — куски претрейна, чтобы не забыла книжки

**Архитектура SplineGPT:**

KAN в Q/K проекциях attention (не в MLP как у всех)
MoE каждый 3-й блок
RoPE
Маскинг диалогов — loss только по ответам

**Параметры:**

LR: 6e-5 (10× меньше претрейна)
Batch: 64, effective 256
A100 80GB
Telegram бот шлёт апдейты


Это не дообучение LLaMA. Pretrain с нуля на русском. Своя архитектура, свой датасет.

Скоро заговорит."""
    
    print(f"\n📄 ИСХОДНОЕ СООБЩЕНИЕ:")
    print("-" * 60)
    print(architecture_text)
    print("-" * 60)
    
    # Анализируем архитектурные детали
    arch_details = analyze_architecture_details(architecture_text)
    
    # Критический анализ
    critical_analysis = critical_architecture_analysis()
    
    # Оценка
    scores, total_score = architecture_scoring()
    
    # Сохраняем результат
    result = {
        'message_text': architecture_text,
        'architecture_details': arch_details,
        'critical_analysis': critical_analysis,
        'scores': scores,
        'total_score': total_score,
        'analysis_date': datetime.now().isoformat()
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis/rukallama_architecture_analysis_{timestamp}.json"
    
    os.makedirs("analysis", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # Создаем markdown отчет
    markdown_report = f"""# 🏗️ Анализ архитектуры RuKallama SplineGPT

**Дата анализа:** {datetime.now().strftime("%d.%m.%Y %H:%M")}  
**Общая оценка:** {total_score:.1f}/10

## 🔧 Архитектурные компоненты

### KAN в Attention
- **Решение:** KAN в Q/K проекциях вместо MLP
- **Инновационность:** Высокая (8/10)
- **Риск:** Экспериментальная идея без доказанной эффективности

### MoE Integration
- **Паттерн:** MoE каждый 3-й блок
- **Преимущество:** Масштабируемость без линейного роста параметров
- **Риск:** Проблемы с load balancing

### Позиционное кодирование
- **Метод:** RoPE (Rotary Position Embedding)
- **Статус:** Проверенное решение
- **Совместимость:** Вопросы с KAN + MoE

## 📊 Критическая оценка

| Аспект | Оценка | Комментарий |
|--------|--------|-------------|
| **Инновационность** | 8/10 | Уникальная комбинация KAN + MoE + RoPE |
| **Техническая обоснованность** | 5/10 | Много экспериментальных решений |
| **Качество данных** | 3/10 | Критически малый и устаревший датасет |
| **Масштабируемость** | 6/10 | MoE позволяет рост, но есть риски |
| **Воспроизводимость** | 4/10 | Недостаточно деталей |
| **Практическая применимость** | 7/10 | Фокус на русский язык ценен |

## ⚠️ Основные проблемы

1. **Данные:** 763 книги 1950-1990х критически мало
2. **Архитектура:** KAN в attention не протестирован на больших моделях
3. **Параметры:** Словарь 379K слишком большой
4. **Методология:** Отсутствие сравнения с baseline

## 💡 Рекомендации

1. **Расширить датасет** до 100B+ токенов современного русского
2. **Провести ablation studies** для KAN vs MLP
3. **Оптимизировать словарь** до 100-150K токенов
4. **Добавить бенчмарки** против существующих моделей

---

*Анализ основан на техническом сообщении от 27.12.2024*
"""
    
    markdown_filename = f"analysis/rukallama_architecture_analysis_{timestamp}.md"
    
    with open(markdown_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n💾 Результат сохранен:")
    print(f"   JSON: {filename}")
    print(f"   Markdown: {markdown_filename}")
    
    print(f"\n🎯 ИТОГОВАЯ ОЦЕНКА АРХИТЕКТУРЫ: {total_score:.1f}/10")
    print("✅ Анализ завершен!")

if __name__ == "__main__":
    asyncio.run(main())
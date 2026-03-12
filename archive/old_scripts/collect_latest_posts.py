#!/usr/bin/env python3
"""
Сбор самых свежих постов из канала @technojnec для обновления анализа
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from telethon import TelegramClient

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

async def collect_latest_posts():
    """Сбор самых свежих постов из канала"""
    
    print("🔍 Сбор самых свежих постов из канала @technojnec...")
    
    # Создаем клиент
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        # Подключаемся
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем канал
        entity = await client.get_entity('technojnec')
        
        # Собираем последние 50 сообщений
        messages = []
        
        print(f"📊 Сбор последних 50 сообщений...")
        
        # Получаем текущее время для фильтрации (с timezone)
        from datetime import timezone
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)
        
        async for message in client.iter_messages(entity, limit=50):
            if message.text:
                message_data = {
                    'id': message.id,
                    'text': message.text,
                    'date': message.date.isoformat() if message.date else None,
                    'views': getattr(message, 'views', 0),
                    'forwards': getattr(message, 'forwards', 0),
                    'replies': getattr(message.replies, 'replies', 0) if message.replies else 0,
                    'is_new': message.date and message.date > last_24h if message.date else False,
                    'is_recent': message.date and message.date > last_week if message.date else False
                }
                
                messages.append(message_data)
                
                # Выводим новые сообщения
                if message_data['is_new']:
                    print(f"\n🆕 НОВОЕ (ID {message.id}, {message_data['views']} просмотров):")
                    print(f"   Дата: {message_data['date']}")
                    print(f"   Текст: {message.text[:200]}...")
                elif message_data['is_recent']:
                    print(f"\n📅 НЕДАВНЕЕ (ID {message.id}, {message_data['views']} просмотров):")
                    print(f"   Дата: {message_data['date']}")
                    print(f"   Текст: {message.text[:150]}...")
        
        # Фильтруем по времени
        new_messages = [msg for msg in messages if msg['is_new']]
        recent_messages = [msg for msg in messages if msg['is_recent']]
        
        print(f"\n📈 СТАТИСТИКА:")
        print(f"   Всего собрано: {len(messages)} сообщений")
        print(f"   Новых (24 часа): {len(new_messages)}")
        print(f"   Недавних (неделя): {len(recent_messages)}")
        
        # Ищем ключевые темы в новых постах
        key_topics = {
            'архитектура': ['архитектур', 'kan', 'moe', 'transformer', 'splinegpt'],
            'бенчмарки': ['бенчмарк', 'тест', 'сравнен', 'против', 'результат', 'метрик'],
            'обучение': ['loss', 'эпоха', 'pretrain', 'finetune', 'обучен'],
            'релиз': ['релиз', 'выпуск', 'готов', 'доступ', 'чат', 'демо'],
            'проблемы': ['ошибк', 'проблем', 'баг', 'исправ', 'починил']
        }
        
        topic_analysis = {}
        for topic, keywords in key_topics.items():
            topic_messages = []
            for msg in new_messages + recent_messages:
                text_lower = msg['text'].lower()
                if any(keyword in text_lower for keyword in keywords):
                    topic_messages.append(msg)
            topic_analysis[topic] = topic_messages
        
        print(f"\n🎯 АНАЛИЗ ТЕМ В НОВЫХ ПОСТАХ:")
        for topic, msgs in topic_analysis.items():
            if msgs:
                print(f"   {topic.upper()}: {len(msgs)} сообщений")
                for msg in msgs[:2]:  # Показываем первые 2
                    print(f"     • ID {msg['id']}: {msg['text'][:100]}...")
        
        # Сохраняем результат
        result = {
            'all_messages': messages,
            'new_messages': new_messages,
            'recent_messages': recent_messages,
            'topic_analysis': topic_analysis,
            'collection_date': datetime.now().isoformat(),
            'stats': {
                'total': len(messages),
                'new_24h': len(new_messages),
                'recent_week': len(recent_messages)
            }
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis/latest_posts_{timestamp}.json"
        
        os.makedirs("analysis", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Результат сохранен в: {filename}")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None
    finally:
        await client.disconnect()

async def analyze_new_developments(data):
    """Анализ новых разработок в проекте"""
    
    if not data:
        return
    
    print(f"\n🔍 АНАЛИЗ НОВЫХ РАЗРАБОТОК")
    print("="*60)
    
    new_messages = data['new_messages']
    recent_messages = data['recent_messages']
    
    if not new_messages and not recent_messages:
        print("❌ Нет новых сообщений для анализа")
        return
    
    # Анализируем прогресс проекта
    progress_indicators = {
        'training_progress': ['loss', 'эпоха', 'step', 'val loss'],
        'architecture_updates': ['архитектур', 'kan', 'moe', 'изменен', 'обновл'],
        'performance_claims': ['быстрее', 'лучше', 'превосход', 'эффективн'],
        'release_signals': ['готов', 'релиз', 'доступ', 'чат', 'демо', 'тест'],
        'problems': ['ошибк', 'проблем', 'не работа', 'баг', 'исправ']
    }
    
    print("📊 ИНДИКАТОРЫ ПРОГРЕССА:")
    
    for indicator, keywords in progress_indicators.items():
        matching_messages = []
        for msg in new_messages + recent_messages:
            text_lower = msg['text'].lower()
            if any(keyword in text_lower for keyword in keywords):
                matching_messages.append(msg)
        
        if matching_messages:
            print(f"\n🎯 {indicator.upper().replace('_', ' ')}:")
            for msg in matching_messages[:3]:  # Показываем первые 3
                print(f"   • ID {msg['id']} ({msg['views']} просмотров)")
                print(f"     {msg['text'][:200]}...")
    
    # Ищем конкретные метрики и цифры
    metrics_found = []
    for msg in new_messages + recent_messages:
        text = msg['text']
        # Ищем loss значения
        import re
        loss_matches = re.findall(r'loss[:\s]*(\d+\.?\d*)', text.lower())
        step_matches = re.findall(r'step[:\s]*(\d+)', text.lower())
        epoch_matches = re.findall(r'эпох[аи][:\s]*(\d+)', text.lower())
        
        if loss_matches or step_matches or epoch_matches:
            metrics_found.append({
                'id': msg['id'],
                'date': msg['date'],
                'views': msg['views'],
                'loss': loss_matches,
                'steps': step_matches,
                'epochs': epoch_matches,
                'text': text[:300]
            })
    
    if metrics_found:
        print(f"\n📈 НАЙДЕННЫЕ МЕТРИКИ:")
        for metric in metrics_found[:5]:
            print(f"   • ID {metric['id']} ({metric['views']} просмотров)")
            if metric['loss']:
                print(f"     Loss: {metric['loss']}")
            if metric['epochs']:
                print(f"     Epochs: {metric['epochs']}")
            if metric['steps']:
                print(f"     Steps: {metric['steps']}")
            print(f"     Текст: {metric['text'][:150]}...")
            print()

async def main():
    """Главная функция"""
    
    print("🔄 ОБНОВЛЕНИЕ АНАЛИЗА ПО НОВЫМ ПОСТАМ")
    print("="*50)
    
    # Собираем свежие данные
    data = await collect_latest_posts()
    
    if data:
        # Анализируем новые разработки
        await analyze_new_developments(data)
        
        print("\n✅ Обновление завершено!")
        print(f"Найдено {data['stats']['new_24h']} новых сообщений за 24 часа")
        print(f"Найдено {data['stats']['recent_week']} сообщений за неделю")
    else:
        print("\n❌ Обновление не удалось")

if __name__ == "__main__":
    asyncio.run(main())
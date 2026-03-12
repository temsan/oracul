#!/usr/bin/env python3
"""
Сбор дополнительных сообщений из канала для поиска baseline сравнений
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

async def collect_recent_messages():
    """Сбор последних сообщений из канала для поиска baseline сравнений"""
    
    print("🔍 Сбор дополнительных сообщений из канала @technojnec...")
    
    # Создаем клиент
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        # Подключаемся
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем канал
        entity = await client.get_entity('technojnec')
        
        # Собираем больше сообщений (последние 200)
        messages = []
        baseline_keywords = ['baseline', 'сравнен', 'против', 'ruBERT', 'ruGPT', 'GPT-2', 'mBERT', 'XLM-R', 'бенчмарк', 'тест', 'результат', 'метрик', 'perplexity', 'BLEU']
        
        print(f"📊 Сбор последних 200 сообщений...")
        
        async for message in client.iter_messages(entity, limit=200):
            if message.text:
                # Проверяем на наличие ключевых слов
                text_lower = message.text.lower()
                has_baseline_keywords = any(keyword.lower() in text_lower for keyword in baseline_keywords)
                
                message_data = {
                    'id': message.id,
                    'text': message.text,
                    'date': message.date.isoformat() if message.date else None,
                    'views': getattr(message, 'views', 0),
                    'forwards': getattr(message, 'forwards', 0),
                    'replies': getattr(message.replies, 'replies', 0) if message.replies else 0,
                    'has_baseline_keywords': has_baseline_keywords
                }
                
                messages.append(message_data)
                
                # Выводим сообщения с ключевыми словами
                if has_baseline_keywords:
                    print(f"\n🎯 НАЙДЕНО (ID {message.id}):")
                    print(f"   Дата: {message_data['date']}")
                    print(f"   Просмотры: {message_data['views']}")
                    print(f"   Текст: {message.text[:200]}...")
        
        # Фильтруем сообщения с baseline ключевыми словами
        baseline_messages = [msg for msg in messages if msg['has_baseline_keywords']]
        
        print(f"\n📈 СТАТИСТИКА:")
        print(f"   Всего собрано: {len(messages)} сообщений")
        print(f"   С baseline ключевыми словами: {len(baseline_messages)}")
        
        # Сохраняем результат
        result = {
            'all_messages': messages,
            'baseline_messages': baseline_messages,
            'collection_date': datetime.now().isoformat(),
            'total_messages': len(messages),
            'baseline_count': len(baseline_messages)
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis/extended_channel_messages_{timestamp}.json"
        
        os.makedirs("analysis", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Результат сохранен в: {filename}")
        
        # Выводим топ сообщения с baseline
        if baseline_messages:
            print(f"\n🔥 ТОП СООБЩЕНИЯ С BASELINE/СРАВНЕНИЯМИ:")
            for i, msg in enumerate(baseline_messages[:5], 1):
                print(f"\n{i}. ID {msg['id']} ({msg['views']} просмотров)")
                print(f"   {msg['text'][:300]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None
    finally:
        await client.disconnect()

async def main():
    """Главная функция"""
    
    print("🔍 ПОИСК BASELINE СРАВНЕНИЙ")
    print("="*50)
    
    result = await collect_recent_messages()
    
    if result:
        print("\n✅ Сбор завершен успешно!")
        print(f"Найдено {result['baseline_count']} сообщений с потенциальными сравнениями")
    else:
        print("\n❌ Сбор не удался")

if __name__ == "__main__":
    asyncio.run(main())
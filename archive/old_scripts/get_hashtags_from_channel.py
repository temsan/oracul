#!/usr/bin/env python3
"""
Получение всех хештегов из канала 1681841249
"""

import asyncio
import os
import re
from collections import Counter
from telethon import TelegramClient

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

async def get_hashtags_from_channel():
    """Получение всех хештегов из канала"""
    
    channel_id = '1681841249'  # @abramova_garmony1
    print(f"🔍 Поиск хештегов в канале {channel_id}...")
    
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем канал
        entity = await client.get_entity(int(channel_id))
        print(f"📺 Канал: {entity.title}")
        
        # Собираем все хештеги
        hashtags = Counter()
        message_count = 0
        
        print("📥 Сбор сообщений и поиск хештегов...")
        
        async for message in client.iter_messages(entity, limit=500):  # Увеличиваем лимит
            if message.text:
                message_count += 1
                
                # Ищем хештеги в тексте
                found_hashtags = re.findall(r'#\w+', message.text, re.IGNORECASE)
                
                for hashtag in found_hashtags:
                    # Нормализуем хештег (приводим к нижнему регистру)
                    normalized_tag = hashtag.lower()
                    hashtags[normalized_tag] += 1
                
                # Показываем прогресс каждые 50 сообщений
                if message_count % 50 == 0:
                    print(f"   Обработано {message_count} сообщений...")
        
        print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print(f"   Всего сообщений: {message_count}")
        print(f"   Найдено уникальных хештегов: {len(hashtags)}")
        
        if hashtags:
            print(f"\n🏷️ ВСЕ ХЕШТЕГИ (по частоте использования):")
            for hashtag, count in hashtags.most_common():
                print(f"   {hashtag}: {count} раз")
        else:
            print("\n❌ Хештеги не найдены в канале")
        
        return dict(hashtags)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        await client.disconnect()

async def main():
    """Главная функция"""
    hashtags = await get_hashtags_from_channel()
    
    if hashtags:
        print(f"\n✅ Анализ завершен! Найдено {len(hashtags)} уникальных хештегов.")
        
        # Сохраняем результат
        import json
        from datetime import datetime
        
        result = {
            'channel_id': '1681841249',
            'channel_username': 'abramova_garmony1',
            'analysis_date': datetime.now().isoformat(),
            'hashtags': hashtags,
            'total_unique_hashtags': len(hashtags),
            'total_hashtag_usage': sum(hashtags.values())
        }
        
        filename = f"analysis/abramova/hashtags_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Результат сохранен в: {filename}")
    else:
        print("\n❌ Хештеги не найдены или произошла ошибка")

if __name__ == "__main__":
    asyncio.run(main())
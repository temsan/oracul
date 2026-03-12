#!/usr/bin/env python3
"""
Получение всех сообщений из диалога с заказчицей 1264917018
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

async def get_client_messages():
    """Получение всех сообщений из диалога с заказчицей"""
    
    client_id = '1264917018'  # @abramova_psychotherapy
    print(f"🔍 Получение сообщений из диалога с заказчицей {client_id}...")
    
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем пользователя
        entity = await client.get_entity(int(client_id))
        print(f"👤 Пользователь: {entity.first_name} {entity.last_name or ''} (@{entity.username})")
        
        # Собираем все сообщения
        messages = []
        message_count = 0
        
        print("📥 Сбор всех сообщений из диалога...")
        
        async for message in client.iter_messages(entity, limit=1000):  # Увеличиваем лимит
            message_count += 1
            
            # Определяем отправителя
            sender = "client" if message.from_id and message.from_id.user_id == int(client_id) else "me"
            
            msg_data = {
                'id': message.id,
                'text': message.text or '',
                'date': message.date.isoformat() if message.date else None,
                'sender': sender,
                'is_voice': bool(message.voice),
                'is_video': bool(message.video),
                'is_photo': bool(message.photo),
                'is_document': bool(message.document),
                'has_links': bool(message.entities and any(e.url for e in message.entities if hasattr(e, 'url'))),
                'word_count': len((message.text or '').split()),
                'char_count': len(message.text or '')
            }
            
            messages.append(msg_data)
            
            # Показываем прогресс каждые 50 сообщений
            if message_count % 50 == 0:
                print(f"   Обработано {message_count} сообщений...")
        
        print(f"\n📊 РЕЗУЛЬТАТЫ СБОРА:")
        print(f"   Всего сообщений: {message_count}")
        
        # Анализируем сообщения
        client_messages = [msg for msg in messages if msg['sender'] == 'client']
        my_messages = [msg for msg in messages if msg['sender'] == 'me']
        
        print(f"   Сообщений от заказчицы: {len(client_messages)}")
        print(f"   Моих сообщений: {len(my_messages)}")
        
        # Показываем последние сообщения от заказчицы
        print(f"\n💬 ПОСЛЕДНИЕ СООБЩЕНИЯ ОТ ЗАКАЗЧИЦЫ:")
        recent_client_messages = [msg for msg in client_messages if msg['text']][:10]
        
        for i, msg in enumerate(recent_client_messages, 1):
            date_str = datetime.fromisoformat(msg['date'].replace('Z', '+00:00')).strftime('%d.%m %H:%M') if msg['date'] else 'Нет даты'
            print(f"\n{i}. [{date_str}] {'🎤' if msg['is_voice'] else '📝'}")
            print(f"   {msg['text'][:200]}{'...' if len(msg['text']) > 200 else ''}")
        
        # Сохраняем результат
        result = {
            'client_id': client_id,
            'client_username': entity.username,
            'client_name': f"{entity.first_name} {entity.last_name or ''}".strip(),
            'analysis_date': datetime.now().isoformat(),
            'total_messages': message_count,
            'client_messages_count': len(client_messages),
            'my_messages_count': len(my_messages),
            'messages': messages
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis/abramova/client_dialog_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Результат сохранен в: {filename}")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await client.disconnect()

async def main():
    """Главная функция"""
    result = await get_client_messages()
    
    if result:
        print(f"\n✅ Анализ завершен!")
        print(f"📊 Всего сообщений: {result['total_messages']}")
        print(f"👤 От заказчицы: {result['client_messages_count']}")
        print(f"🤖 Моих ответов: {result['my_messages_count']}")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
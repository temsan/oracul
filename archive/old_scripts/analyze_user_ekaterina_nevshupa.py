#!/usr/bin/env python3
"""
Анализ пользователя Екатерина Невшупа (ID: 8466654094)
"""

import asyncio
import os
import json
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import User
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

async def analyze_user_ekaterina_nevshupa():
    """Анализ пользователя Екатерина Невшупа"""
    
    user_id = 8466654094
    print(f"🔮 Анализ пользователя Екатерина Невшупа (ID: {user_id})...")
    
    # Создаем клиент
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        # Подключаемся
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем информацию о пользователе
        try:
            user = await client.get_entity(user_id)
        except Exception as e:
            print(f"❌ Не удалось получить информацию о пользователе: {e}")
            return None
        
        # Базовая информация о пользователе
        user_info = {
            'id': user.id,
            'first_name': getattr(user, 'first_name', None),
            'last_name': getattr(user, 'last_name', None),
            'username': getattr(user, 'username', None),
            'phone': getattr(user, 'phone', None),
            'is_bot': getattr(user, 'bot', False),
            'is_verified': getattr(user, 'verified', False),
            'is_premium': getattr(user, 'premium', False),
            'is_scam': getattr(user, 'scam', False),
            'is_fake': getattr(user, 'fake', False),
            'is_contact': getattr(user, 'contact', False),
            'is_mutual_contact': getattr(user, 'mutual_contact', False),
            'status': str(getattr(user, 'status', 'Unknown')),
            'lang_code': getattr(user, 'lang_code', None)
        }
        
        print(f"\n👤 ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:")
        print(f"   ID: {user_info['id']}")
        print(f"   Имя: {user_info['first_name'] or 'Не указано'}")
        print(f"   Фамилия: {user_info['last_name'] or 'Не указано'}")
        print(f"   Username: @{user_info['username'] or 'Не указан'}")
        print(f"   Телефон: {user_info['phone'] or 'Скрыт'}")
        print(f"   Бот: {'Да' if user_info['is_bot'] else 'Нет'}")
        print(f"   Верифицирован: {'Да' if user_info['is_verified'] else 'Нет'}")
        print(f"   Premium: {'Да' if user_info['is_premium'] else 'Нет'}")
        print(f"   Контакт: {'Да' if user_info['is_contact'] else 'Нет'}")
        print(f"   Статус: {user_info['status']}")
        print(f"   Язык: {user_info['lang_code'] or 'Не указан'}")
        
        # Пытаемся получить общие чаты
        common_chats = []
        try:
            common_chats_result = await client.get_common_chats(user)
            for chat in common_chats_result:
                common_chats.append({
                    'id': chat.id,
                    'title': getattr(chat, 'title', 'Unknown'),
                    'type': 'channel' if hasattr(chat, 'broadcast') else 'group'
                })
            
            print(f"\n💬 ОБЩИЕ ЧАТЫ ({len(common_chats)}):")
            for chat in common_chats[:10]:  # Показываем первые 10
                print(f"   {chat['title']} ({chat['type']})")
                
        except Exception as e:
            print(f"\n💬 ОБЩИЕ ЧАТЫ: Не удалось получить ({e})")
        
        # Пытаемся получить историю сообщений (если есть диалог)
        messages = []
        try:
            print(f"\n📊 Получение истории сообщений...")
            async for message in client.iter_messages(user, limit=50):
                if message.text:
                    messages.append({
                        'id': message.id,
                        'text': message.text,
                        'date': message.date.isoformat() if message.date else None,
                        'from_id': message.from_id.user_id if message.from_id else None,
                        'is_outgoing': message.out
                    })
            
            print(f"✅ Получено {len(messages)} сообщений")
            
            if messages:
                print(f"\n📝 ПОСЛЕДНИЕ СООБЩЕНИЯ:")
                for msg in messages[:5]:  # Показываем первые 5
                    direction = "→" if msg['is_outgoing'] else "←"
                    date = msg['date'][:16] if msg['date'] else 'Unknown'
                    text = msg['text'][:100] + '...' if len(msg['text']) > 100 else msg['text']
                    print(f"   [{date}] {direction} {text}")
                    
        except UserPrivacyRestrictedError:
            print(f"🔒 История сообщений недоступна (настройки приватности)")
        except Exception as e:
            print(f"❌ Ошибка получения сообщений: {e}")
        
        # Анализ активности
        analysis = {
            'total_messages': len(messages),
            'has_dialog': len(messages) > 0,
            'common_chats_count': len(common_chats),
            'is_accessible': True,
            'privacy_level': 'open' if messages else 'restricted'
        }
        
        if messages:
            # Анализ текста
            all_text = ' '.join([msg['text'] for msg in messages])
            words = all_text.split()
            
            # Подсчет исходящих/входящих
            outgoing = sum(1 for msg in messages if msg['is_outgoing'])
            incoming = len(messages) - outgoing
            
            analysis.update({
                'total_words': len(words),
                'avg_message_length': len(all_text) / len(messages),
                'outgoing_messages': outgoing,
                'incoming_messages': incoming,
                'communication_ratio': outgoing / incoming if incoming > 0 else 0
            })
            
            # Частотный анализ слов
            word_freq = {}
            for word in words:
                if len(word) > 3:
                    word_lower = word.lower().strip('.,!?;:"()[]{}')
                    word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            analysis['top_words'] = top_words
            
            print(f"\n📈 АНАЛИЗ АКТИВНОСТИ:")
            print(f"   Всего сообщений: {analysis['total_messages']}")
            print(f"   Исходящих: {analysis['outgoing_messages']}")
            print(f"   Входящих: {analysis['incoming_messages']}")
            print(f"   Средняя длина: {analysis['avg_message_length']:.1f} символов")
            print(f"   Общих чатов: {analysis['common_chats_count']}")
            
            if top_words:
                print(f"\n🔤 ТОП-10 СЛОВ:")
                for word, count in top_words:
                    print(f"   {word}: {count}")
        
        # Сохраняем результат
        result = {
            'user_info': user_info,
            'common_chats': common_chats,
            'messages_sample': messages[:20],  # Первые 20 сообщений
            'analysis': analysis,
            'analysis_date': datetime.now().isoformat()
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создаем папку для пользователя
        os.makedirs("analysis/user_profiles", exist_ok=True)
        filename = f"analysis/user_profiles/user_ekaterina_nevshupa_analysis_{timestamp}.json"
        
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
    print("🔮 АНАЛИЗ ПОЛЬЗОВАТЕЛЯ ЕКАТЕРИНА НЕВШУПА")
    print("="*50)
    
    result = await analyze_user_ekaterina_nevshupa()
    
    if result:
        print("\n✅ Анализ завершен успешно!")
        print(f"👤 Пользователь: {result['user_info']['first_name']} {result['user_info']['last_name'] or ''}")
        print(f"📊 Сообщений: {result['analysis']['total_messages']}")
        print(f"💬 Общих чатов: {result['analysis']['common_chats_count']}")
        print(f"🔒 Приватность: {result['analysis']['privacy_level']}")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
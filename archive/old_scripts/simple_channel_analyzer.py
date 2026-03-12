#!/usr/bin/env python3
"""
Простой анализатор канала 2402063854 без зависимостей от oracul-bot
"""

import asyncio
import os
import json
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

async def analyze_channel_simple(channel_id: str):
    """Простой анализ канала"""
    
    print(f"🔮 Анализ канала {channel_id}...")
    
    # Создаем клиент
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        # Подключаемся
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем информацию о канале
        try:
            entity = await client.get_entity(int(channel_id))
        except ValueError:
            # Если не число, пробуем как username
            entity = await client.get_entity(channel_id)
        
        # Базовая информация
        channel_info = {
            'id': entity.id,
            'title': getattr(entity, 'title', 'Unknown'),
            'username': getattr(entity, 'username', None),
            'type': 'channel' if isinstance(entity, Channel) else 'group',
            'participants_count': getattr(entity, 'participants_count', 0),
            'description': getattr(entity, 'about', ''),
            'verified': getattr(entity, 'verified', False),
            'scam': getattr(entity, 'scam', False)
        }
        
        print(f"\n📺 ИНФОРМАЦИЯ О КАНАЛЕ:")
        print(f"   Название: {channel_info['title']}")
        print(f"   ID: {channel_info['id']}")
        print(f"   Username: @{channel_info['username'] or 'Не указан'}")
        print(f"   Тип: {channel_info['type']}")
        print(f"   Подписчиков: {channel_info['participants_count'] or 0:,}")
        print(f"   Верифицирован: {'Да' if channel_info['verified'] else 'Нет'}")
        print(f"   Описание: {(channel_info['description'] or 'Отсутствует')[:200]}...")
        
        # Собираем сообщения
        messages = []
        message_count = 0
        total_views = 0
        total_forwards = 0
        total_replies = 0
        
        print(f"\n📊 Сбор сообщений...")
        
        async for message in client.iter_messages(entity, limit=100):
            if message.text:
                message_count += 1
                total_views += getattr(message, 'views', 0)
                total_forwards += getattr(message, 'forwards', 0)
                total_replies += getattr(message.replies, 'replies', 0) if message.replies else 0
                
                messages.append({
                    'id': message.id,
                    'text': message.text,
                    'date': message.date.isoformat() if message.date else None,
                    'views': getattr(message, 'views', 0),
                    'forwards': getattr(message, 'forwards', 0),
                    'replies': getattr(message.replies, 'replies', 0) if message.replies else 0
                })
        
        # Статистика
        all_text = ' '.join([msg['text'] for msg in messages])
        words = all_text.split()
        
        stats = {
            'total_messages': message_count,
            'total_characters': len(all_text),
            'total_words': len(words),
            'avg_message_length': len(all_text) / message_count if message_count > 0 else 0,
            'total_views': total_views,
            'total_forwards': total_forwards,
            'total_replies': total_replies,
            'avg_views': total_views / message_count if message_count > 0 else 0,
            'engagement_rate': (total_forwards + total_replies) / total_views * 100 if total_views > 0 else 0
        }
        
        print(f"\n📈 СТАТИСТИКА:")
        print(f"   Проанализировано сообщений: {stats['total_messages']}")
        print(f"   Общее количество символов: {stats['total_characters']:,}")
        print(f"   Общее количество слов: {stats['total_words']:,}")
        print(f"   Средняя длина сообщения: {stats['avg_message_length']:.1f} символов")
        print(f"   Общие просмотры: {stats['total_views']:,}")
        print(f"   Общие репосты: {stats['total_forwards']:,}")
        print(f"   Общие ответы: {stats['total_replies']:,}")
        print(f"   Средние просмотры: {stats['avg_views']:.1f}")
        print(f"   Коэффициент вовлеченности: {stats['engagement_rate']:.2f}%")
        
        # Анализ ключевых слов
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_lower = word.lower()
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
        
        print(f"\n🔤 ТОП-15 СЛОВ:")
        for word, count in top_words:
            print(f"   {word}: {count}")
        
        # Анализ тематики
        business_keywords = ['бизнес', 'стартап', 'деньги', 'инвестиции', 'продажи', 'маркетинг', 'доход']
        tech_keywords = ['технологии', 'ai', 'ии', 'программирование', 'разработка', 'код', 'нейросеть']
        career_keywords = ['карьера', 'работа', 'резюме', 'собеседование', 'навыки', 'вакансия']
        personal_keywords = ['развитие', 'мотивация', 'цели', 'успех', 'личность', 'рост']
        
        text_lower = all_text.lower()
        categories = {
            'Бизнес': sum(text_lower.count(word) for word in business_keywords),
            'Технологии': sum(text_lower.count(word) for word in tech_keywords),
            'Карьера': sum(text_lower.count(word) for word in career_keywords),
            'Личное развитие': sum(text_lower.count(word) for word in personal_keywords)
        }
        
        print(f"\n🏷️ ТЕМАТИЧЕСКИЕ КАТЕГОРИИ:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"   {category}: {count} упоминаний")
        
        # Сохраняем результат
        result = {
            'channel_info': channel_info,
            'statistics': stats,
            'top_words': top_words,
            'categories': categories,
            'messages_sample': messages[:10],  # Первые 10 сообщений как пример
            'analysis_date': datetime.now().isoformat()
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis/channel_{channel_id}_analysis_{timestamp}.json"
        
        os.makedirs("analysis", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Результат сохранен в: {filename}")
        
        return result
        
    except ChannelPrivateError:
        print("❌ Канал приватный или недоступен")
        return None
    except ChatAdminRequiredError:
        print("❌ Требуются права администратора для анализа")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await client.disconnect()

async def main():
    """Главная функция"""
    print("🔮 ORACUL CHANNEL ANALYZER")
    print("="*50)
    
    # Анализируем канал 2402063854
    result = await analyze_channel_simple('2402063854')
    
    if result:
        print("\n✅ Анализ завершен успешно!")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
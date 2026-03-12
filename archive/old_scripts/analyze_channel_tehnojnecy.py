#!/usr/bin/env python3
"""
Анализатор канала 2405169642
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

async def analyze_channel_tehnojnecy():
    """Анализ канала "Техножнецы" """
    
    channel_id = '2405169642'
    print(f"🔮 Анализ канала Техножнецы...")
    
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
        
        # Собираем сообщения (больше для детального анализа)
        messages = []
        message_count = 0
        total_views = 0
        total_forwards = 0
        total_replies = 0
        
        print(f"\n📊 Сбор сообщений...")
        
        async for message in client.iter_messages(entity, limit=200):  # Увеличил лимит
            if message.text:
                message_count += 1
                views = getattr(message, 'views', 0) or 0
                forwards = getattr(message, 'forwards', 0) or 0
                replies = getattr(message.replies, 'replies', 0) if message.replies else 0
                
                total_views += views
                total_forwards += forwards
                total_replies += replies
                
                messages.append({
                    'id': message.id,
                    'text': message.text,
                    'date': message.date.isoformat() if message.date else None,
                    'views': views,
                    'forwards': forwards,
                    'replies': replies
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
                word_lower = word.lower().strip('.,!?;:"()[]{}')
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        print(f"\n🔤 ТОП-20 СЛОВ:")
        for word, count in top_words:
            print(f"   {word}: {count}")
        
        # Расширенный анализ тематики
        business_keywords = ['бизнес', 'стартап', 'деньги', 'инвестиции', 'продажи', 'маркетинг', 'доход', 'прибыль', 'капитал']
        tech_keywords = ['технологии', 'ai', 'ии', 'программирование', 'разработка', 'код', 'нейросеть', 'алгоритм', 'данные']
        career_keywords = ['карьера', 'работа', 'резюме', 'собеседование', 'навыки', 'вакансия', 'профессия', 'специалист']
        personal_keywords = ['развитие', 'мотивация', 'цели', 'успех', 'личность', 'рост', 'саморазвитие', 'обучение']
        finance_keywords = ['финансы', 'банк', 'кредит', 'депозит', 'валюта', 'курс', 'экономика', 'рынок']
        crypto_keywords = ['криптовалюта', 'биткоин', 'блокчейн', 'майнинг', 'токен', 'nft', 'defi']
        
        text_lower = all_text.lower()
        categories = {
            'Бизнес': sum(text_lower.count(word) for word in business_keywords),
            'Технологии': sum(text_lower.count(word) for word in tech_keywords),
            'Карьера': sum(text_lower.count(word) for word in career_keywords),
            'Личное развитие': sum(text_lower.count(word) for word in personal_keywords),
            'Финансы': sum(text_lower.count(word) for word in finance_keywords),
            'Криптовалюты': sum(text_lower.count(word) for word in crypto_keywords)
        }
        
        print(f"\n🏷️ ТЕМАТИЧЕСКИЕ КАТЕГОРИИ:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"   {category}: {count} упоминаний")
        
        # Анализ активности по времени
        dates = [datetime.fromisoformat(msg['date'].replace('Z', '+00:00')) for msg in messages if msg['date']]
        if dates:
            latest_date = max(dates)
            earliest_date = min(dates)
            days_active = (latest_date - earliest_date).days
            
            print(f"\n📅 ВРЕМЕННАЯ АКТИВНОСТЬ:")
            print(f"   Период анализа: {earliest_date.strftime('%Y-%m-%d')} - {latest_date.strftime('%Y-%m-%d')}")
            print(f"   Дней активности: {days_active}")
            print(f"   Сообщений в день: {stats['total_messages'] / max(days_active, 1):.1f}")
        
        # Поиск популярных сообщений
        popular_messages = sorted(messages, key=lambda x: x['views'], reverse=True)[:5]
        
        print(f"\n🔥 ТОП-5 ПОПУЛЯРНЫХ СООБЩЕНИЙ:")
        for i, msg in enumerate(popular_messages, 1):
            print(f"   {i}. ID {msg['id']}: {msg['views']} просмотров")
            print(f"      {msg['text'][:100]}...")
            print()
        
        # Сохраняем результат
        result = {
            'channel_info': channel_info,
            'statistics': stats,
            'top_words': top_words,
            'categories': categories,
            'popular_messages': popular_messages,
            'all_messages': messages,  # Сохраняем все сообщения для дальнейшего анализа
            'analysis_date': datetime.now().isoformat()
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создаем папку для канала
        os.makedirs("analysis/channel_research", exist_ok=True)
        filename = f"analysis/channel_research/channel_tehnojnecy_analysis_{timestamp}.json"
        
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
    print("🔮 АНАЛИЗ КАНАЛА ТЕХНОЖНЕЦЫ")
    print("="*50)
    
    result = await analyze_channel_tehnojnecy()
    
    if result:
        print("\n✅ Анализ завершен успешно!")
        print(f"📊 Проанализировано {result['statistics']['total_messages']} сообщений")
        print(f"👥 Подписчиков: {result['channel_info']['participants_count']:,}")
        print(f"📈 Средняя вовлеченность: {result['statistics']['engagement_rate']:.2f}%")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
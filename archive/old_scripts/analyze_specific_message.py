#!/usr/bin/env python3
"""
Анализ конкретного сообщения из Telegram канала по ссылке
Пример: https://t.me/technojnec/2598
"""

import asyncio
import os
import json
import re
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError
import openai

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

# OpenRouter для LLM анализа
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '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')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'openai/gpt-oss-20b:free')

def parse_telegram_link(link: str):
    """Парсинг Telegram ссылки для извлечения канала и ID сообщения"""
    
    # Паттерны для разных форматов ссылок
    patterns = [
        r'https://t\.me/([^/]+)/(\d+)',  # https://t.me/channel/123
        r'https://telegram\.me/([^/]+)/(\d+)',  # https://telegram.me/channel/123
        r't\.me/([^/]+)/(\d+)',  # t.me/channel/123
        r'@([^/]+)/(\d+)',  # @channel/123
    ]
    
    for pattern in patterns:
        match = re.match(pattern, link.strip())
        if match:
            channel = match.group(1)
            message_id = int(match.group(2))
            return channel, message_id
    
    return None, None

async def get_specific_message(channel_username: str, message_id: int):
    """Получение конкретного сообщения из канала"""
    
    print(f"🔍 Получение сообщения {message_id} из канала @{channel_username}...")
    
    # Создаем клиент
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        # Подключаемся
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем канал
        try:
            if channel_username.isdigit():
                entity = await client.get_entity(int(channel_username))
            else:
                entity = await client.get_entity(channel_username)
        except Exception as e:
            print(f"❌ Ошибка получения канала: {e}")
            return None
        
        # Получаем конкретное сообщение
        try:
            message = await client.get_messages(entity, ids=message_id)
            
            if not message or not message.text:
                print(f"❌ Сообщение {message_id} не найдено или не содержит текст")
                return None
            
            # Формируем данные сообщения
            message_data = {
                'id': message.id,
                'text': message.text,
                'date': message.date.isoformat() if message.date else None,
                'views': getattr(message, 'views', 0),
                'forwards': getattr(message, 'forwards', 0),
                'replies': getattr(message.replies, 'replies', 0) if message.replies else 0,
                'reactions': extract_reactions(message),
                'channel_info': {
                    'id': entity.id,
                    'title': getattr(entity, 'title', 'Unknown'),
                    'username': getattr(entity, 'username', None),
                    'participants_count': getattr(entity, 'participants_count', 0)
                }
            }
            
            print(f"\n📄 СООБЩЕНИЕ ПОЛУЧЕНО:")
            print(f"   ID: {message_data['id']}")
            print(f"   Дата: {message_data['date']}")
            print(f"   Просмотры: {message_data['views']:,}")
            print(f"   Репосты: {message_data['forwards']}")
            print(f"   Ответы: {message_data['replies']}")
            print(f"   Длина текста: {len(message_data['text'])} символов")
            
            return message_data
            
        except Exception as e:
            print(f"❌ Ошибка получения сообщения: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return None
    finally:
        await client.disconnect()

def extract_reactions(message):
    """Извлечение реакций из сообщения"""
    reactions = {}
    
    if hasattr(message, 'reactions') and message.reactions:
        for reaction in message.reactions.results:
            emoji = reaction.reaction.emoticon if hasattr(reaction.reaction, 'emoticon') else str(reaction.reaction)
            reactions[emoji] = reaction.count
    
    return reactions

async def analyze_message_with_llm(message_data: dict):
    """Анализ сообщения с помощью LLM"""
    
    if not OPENROUTER_API_KEY:
        print("❌ Не найден OPENROUTER_API_KEY")
        return None
    
    print("🤖 Анализ сообщения с помощью LLM...")
    
    client = openai.AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )
    
    # Формируем промпт для анализа
    analysis_prompt = f"""
    Проанализируй это сообщение из Telegram канала "{message_data['channel_info']['title']}":

    ТЕКСТ СООБЩЕНИЯ:
    "{message_data['text']}"

    МЕТАДАННЫЕ:
    - ID сообщения: {message_data['id']}
    - Дата: {message_data['date']}
    - Просмотры: {message_data['views']:,}
    - Репосты: {message_data['forwards']}
    - Ответы: {message_data['replies']}

    Проведи глубокий анализ по следующим аспектам:

    1. СОДЕРЖАНИЕ И ТЕМАТИКА:
    - Основная тема сообщения
    - Ключевые идеи и концепции
    - Технические детали (если есть)

    2. СТИЛЬ И ТОН:
    - Стиль изложения (научный, популярный, личный)
    - Эмоциональная окраска
    - Целевая аудитория

    3. КОНТЕКСТ И ЗНАЧИМОСТЬ:
    - Важность информации
    - Актуальность для сферы
    - Потенциальное влияние

    4. КАЧЕСТВО КОНТЕНТА:
    - Информативность (1-10)
    - Достоверность утверждений
    - Практическая ценность

    5. ВОВЛЕЧЕННОСТЬ АУДИТОРИИ:
    - Анализ метрик (просмотры, репосты, ответы)
    - Причины интереса аудитории
    - Потенциал виральности

    Дай развернутый анализ на русском языке.
    """
    
    try:
        response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "Ты эксперт по анализу контента и коммуникаций. Твоя задача - дать глубокий и объективный анализ сообщения, учитывая его содержание, контекст и метрики вовлеченности."
                },
                {
                    "role": "user", 
                    "content": analysis_prompt
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        analysis_result = response.choices[0].message.content
        
        print("\n" + "="*80)
        print("🧠 LLM АНАЛИЗ СООБЩЕНИЯ")
        print("="*80)
        print(analysis_result)
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ Ошибка LLM анализа: {e}")
        return None

async def analyze_telegram_message(telegram_link: str):
    """Основная функция анализа сообщения по ссылке"""
    
    print("🔮 АНАЛИЗ КОНКРЕТНОГО СООБЩЕНИЯ")
    print("="*50)
    print(f"Ссылка: {telegram_link}")
    
    # Парсим ссылку
    channel, message_id = parse_telegram_link(telegram_link)
    
    if not channel or not message_id:
        print("❌ Не удалось распарсить ссылку")
        print("Поддерживаемые форматы:")
        print("  - https://t.me/channel/123")
        print("  - https://telegram.me/channel/123")
        print("  - t.me/channel/123")
        print("  - @channel/123")
        return None
    
    print(f"📺 Канал: @{channel}")
    print(f"📄 ID сообщения: {message_id}")
    
    # Получаем сообщение
    message_data = await get_specific_message(channel, message_id)
    
    if not message_data:
        return None
    
    # Показываем текст сообщения
    print(f"\n📝 ТЕКСТ СООБЩЕНИЯ:")
    print("-" * 60)
    print(message_data['text'])
    print("-" * 60)
    
    # Анализируем с помощью LLM
    llm_analysis = await analyze_message_with_llm(message_data)
    
    # Сохраняем результат
    result = {
        'message_data': message_data,
        'llm_analysis': llm_analysis,
        'analysis_date': datetime.now().isoformat(),
        'source_link': telegram_link
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis/message_{channel}_{message_id}_analysis_{timestamp}.json"
    
    os.makedirs("analysis", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    # Создаем markdown отчет
    markdown_report = f"""# 📄 Анализ сообщения из канала @{channel}

**Ссылка:** {telegram_link}  
**ID сообщения:** {message_id}  
**Дата анализа:** {datetime.now().strftime("%d.%m.%Y %H:%M")}

## 📊 Метрики сообщения

- **Просмотры:** {message_data['views']:,}
- **Репосты:** {message_data['forwards']}
- **Ответы:** {message_data['replies']}
- **Дата публикации:** {message_data['date']}

## 📝 Текст сообщения

```
{message_data['text']}
```

## 🧠 LLM Анализ

{llm_analysis or 'Анализ не выполнен'}

---

*Анализ выполнен с помощью Oracul Engine*
"""
    
    markdown_filename = f"analysis/message_{channel}_{message_id}_analysis_{timestamp}.md"
    
    with open(markdown_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n💾 Результат сохранен:")
    print(f"   JSON: {filename}")
    print(f"   Markdown: {markdown_filename}")
    
    return result

async def main():
    """Главная функция"""
    
    # Анализируем конкретное сообщение
    telegram_link = "https://t.me/technojnec/2598"
    
    result = await analyze_telegram_message(telegram_link)
    
    if result:
        print("\n✅ Анализ завершен успешно!")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
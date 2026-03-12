"""
Поиск контакта для вакансии ЮК Импульс в конкретном канале
"""
import asyncio
from telethon import TelegramClient
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Пробуем разные варианты ID
CHANNEL_IDS = [
    1595873656,
    -1001595873656,
    -1001595873656
]

VACANCY_KEYWORDS = [
    "129381806",
    "ЮК Импульс",
    "UK Impulse",
    "импульс",
    "impulse",
    "ai engineer владимир",
    "владимир ai",
    "120000",
    "120 000"
]

async def search_in_channel(client, channel_id):
    """Поиск в конкретном канале"""
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Проверяю канал ID: {channel_id}")
        print(f"{'='*60}")
        
        channel = await client.get_entity(channel_id)
        print(f"✅ Канал найден: {channel.title}")
        if hasattr(channel, 'username') and channel.username:
            print(f"   @{channel.username}")
        print(f"   ID: {channel.id}")
        
        # Показываем последние 5 сообщений для понимания контента
        print(f"\n📋 Последние 5 сообщений:")
        recent = await client.get_messages(channel, limit=5)
        for i, msg in enumerate(recent, 1):
            if msg.text:
                print(f"\n{i}. {msg.date.strftime('%d.%m.%Y')}: {msg.text[:100]}...")
        
        # Поиск по ключевым словам
        print(f"\n🔎 Поиск вакансии ЮК Импульс...")
        found = False
        
        async for message in client.iter_messages(channel, limit=1000):
            if message.text:
                text_lower = message.text.lower()
                
                # Проверяем ключевые слова
                if any(kw.lower() in text_lower for kw in VACANCY_KEYWORDS):
                    found = True
                    print(f"\n{'🎯'*20}")
                    print(f"✅ НАЙДЕНО!")
                    print(f"{'🎯'*20}")
                    print(f"\nДата: {message.date.strftime('%d.%m.%Y %H:%M')}")
                    print(f"ID сообщения: {message.id}")
                    
                    if hasattr(channel, 'username') and channel.username:
                        print(f"Ссылка: https://t.me/{channel.username}/{message.id}")
                    else:
                        print(f"Ссылка: https://t.me/c/{str(channel.id)[4:]}/{message.id}")
                    
                    print(f"\n📝 Текст сообщения:")
                    print(f"{'-'*60}")
                    print(message.text)
                    print(f"{'-'*60}")
                    
                    # Извлекаем контакты
                    print(f"\n📞 КОНТАКТЫ:")
                    
                    # Telegram
                    tg = re.findall(r'@([a-zA-Z0-9_]{5,32})', message.text)
                    if tg:
                        print(f"   Telegram: {', '.join(['@' + c for c in tg])}")
                    
                    # Email
                    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message.text)
                    if emails:
                        print(f"   Email: {', '.join(emails)}")
                    
                    # Телефон
                    phones = re.findall(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', message.text)
                    valid_phones = [p for p in phones if len(re.sub(r'[^0-9]', '', p)) >= 10]
                    if valid_phones:
                        print(f"   Телефон: {', '.join(valid_phones)}")
                    
                    # Кнопки
                    if message.buttons:
                        print(f"\n   🔘 Кнопки:")
                        for row in message.buttons:
                            for button in row:
                                print(f"      • {button.text}")
                                if button.url:
                                    print(f"        {button.url}")
                    
                    print(f"\n{'='*60}\n")
                    break
        
        if not found:
            print(f"\n❌ Вакансия не найдена в последних 1000 сообщениях")
        
        return found
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def main():
    client = TelegramClient('oracul', 
                           int(os.getenv('TG_API_ID')), 
                           os.getenv('TG_API_HASH'))
    
    await client.start()
    
    print("🔍 ПОИСК ВАКАНСИИ ЮК ИМПУЛЬС")
    print("="*60)
    
    # Пробуем все варианты ID
    found = False
    for channel_id in CHANNEL_IDS:
        result = await search_in_channel(client, channel_id)
        if result:
            found = True
            break
    
    if not found:
        print(f"\n\n💡 АЛЬТЕРНАТИВНЫЕ СПОСОБЫ:")
        print(f"   1. Проверь вакансию на HH.ru - там может быть контакт рекрутера")
        print(f"   2. Найди компанию 'ЮК Импульс' в LinkedIn/Telegram")
        print(f"   3. Поищи в Google: 'ЮК Импульс Владимир AI вакансии'")
        print(f"   4. Проверь, может ID канала был указан неверно")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())

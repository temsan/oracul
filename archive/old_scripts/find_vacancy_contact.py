"""
Скрипт для поиска контактов по вакансии в Telegram канале
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel
import os
from dotenv import load_dotenv
import re

load_dotenv()

# ID канала и ключевые слова для поиска
CHANNEL_ID = -1001595873656  # Добавляем префикс для канала
VACANCY_URL = "https://spb.hh.ru/vacancy/129381806"
VACANCY_ID = "129381806"

# Ключевые слова для поиска вакансии
KEYWORDS = [
    VACANCY_ID,
    "129381806",
    "ЮК Импульс",
    "UK Impulse",
    "AI Engineer",
    "LLM Engineer"
]

async def main():
    client = TelegramClient('oracul', 
                           int(os.getenv('TG_API_ID')), 
                           os.getenv('TG_API_HASH'))
    
    await client.start()
    
    print(f"🔍 Поиск вакансии {VACANCY_ID} в канале {CHANNEL_ID}...\n")
    
    try:
        # Получаем канал
        channel = await client.get_entity(CHANNEL_ID)
        print(f"📢 Канал: {channel.title}")
        print(f"   Username: @{channel.username if channel.username else 'нет'}")
        print(f"   ID: {channel.id}\n")
        
        # Ищем сообщения с вакансией
        print("🔎 Поиск сообщений с вакансией...")
        print("-" * 60)
        
        found_messages = []
        
        # Сначала покажем последние 10 сообщений для понимания формата
        print("\n📋 Последние 10 сообщений в канале:")
        recent_messages = await client.get_messages(channel, limit=10)
        for i, msg in enumerate(recent_messages, 1):
            if msg.text:
                print(f"\n{i}. {msg.date.strftime('%d.%m.%Y %H:%M')}")
                print(f"   {msg.text[:150]}...")
        
        print("\n" + "=" * 60)
        print("🔍 Поиск по ключевым словам...")
        print("=" * 60)
        
        # Поиск по ID вакансии
        async for message in client.iter_messages(channel, limit=1000):
            if message.text:
                text = message.text.lower()
                
                # Проверяем наличие ID вакансии или ключевых слов
                if VACANCY_ID in message.text or any(keyword.lower() in text for keyword in KEYWORDS):
                    found_messages.append(message)
                    
                    print(f"\n✅ Найдено сообщение (ID: {message.id})")
                    print(f"   Дата: {message.date.strftime('%d.%m.%Y %H:%M')}")
                    print(f"   Текст: {message.text[:300]}...")
                    
                    # Ищем контакты в тексте
                    contacts = extract_contacts(message.text)
                    if contacts:
                        print(f"\n   📞 Найденные контакты:")
                        for contact_type, contact_value in contacts.items():
                            print(f"      {contact_type}: {contact_value}")
                    
                    # Проверяем кнопки
                    if message.buttons:
                        print(f"\n   🔘 Кнопки:")
                        for row in message.buttons:
                            for button in row:
                                print(f"      • {button.text}")
                                if button.url:
                                    print(f"        URL: {button.url}")
                    
                    print("-" * 60)
        
        if not found_messages:
            print("\n❌ Вакансия не найдена в последних 500 сообщениях")
            print("\n💡 Попробуем поиск по всему каналу...")
            
            # Расширенный поиск
            search_queries = ["ЮК Импульс", "UK Impulse", "AI Engineer"]
            for query in search_queries:
                print(f"\n🔍 Поиск по запросу: '{query}'")
                results = await client.get_messages(channel, search=query, limit=10)
                
                for msg in results:
                    if msg.text:
                        print(f"\n   • {msg.date.strftime('%d.%m.%Y')}: {msg.text[:200]}...")
                        contacts = extract_contacts(msg.text)
                        if contacts:
                            print(f"     Контакты: {contacts}")
        
        # Информация о канале
        print(f"\n\n📊 Информация о канале:")
        print(f"   Подписчиков: {channel.participants_count if hasattr(channel, 'participants_count') else 'N/A'}")
        
        # Получаем описание канала
        full_channel = await client.get_entity(channel)
        if hasattr(full_channel, 'about'):
            print(f"   Описание: {full_channel.about[:200]}...")
            contacts = extract_contacts(full_channel.about)
            if contacts:
                print(f"\n   📞 Контакты из описания:")
                for contact_type, contact_value in contacts.items():
                    print(f"      {contact_type}: {contact_value}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    await client.disconnect()

def extract_contacts(text):
    """Извлекает контакты из текста"""
    contacts = {}
    
    # Telegram username
    telegram_pattern = r'@([a-zA-Z0-9_]{5,32})'
    telegram_matches = re.findall(telegram_pattern, text)
    if telegram_matches:
        contacts['Telegram'] = ', '.join([f"@{m}" for m in telegram_matches])
    
    # Email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        contacts['Email'] = ', '.join(email_matches)
    
    # Телефон
    phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    phone_matches = re.findall(phone_pattern, text)
    if phone_matches:
        # Фильтруем слишком короткие номера
        valid_phones = [p for p in phone_matches if len(re.sub(r'[^0-9]', '', p)) >= 10]
        if valid_phones:
            contacts['Телефон'] = ', '.join(valid_phones)
    
    # URL
    url_pattern = r'https?://[^\s]+'
    url_matches = re.findall(url_pattern, text)
    if url_matches:
        contacts['URL'] = ', '.join(url_matches)
    
    return contacts

if __name__ == '__main__':
    asyncio.run(main())

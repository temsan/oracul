"""
Поиск вакансии в популярных job-каналах
"""
import asyncio
from telethon import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

# Популярные каналы с вакансиями
JOB_CHANNELS = [
    '@it_jobs_russia',
    '@python_jobs',
    '@ai_jobs_russia',
    '@ml_jobs',
    '@remote_jobs_russia',
    '@devjobs',
    '@career_it',
    '@vacancies_it',
    '@job_python',
    '@ai_ml_jobs'
]

VACANCY_KEYWORDS = [
    "129381806",
    "ЮК Импульс",
    "UK Impulse",
    "импульс ai",
    "impulse ai engineer"
]

async def main():
    client = TelegramClient('oracul', 
                           int(os.getenv('TG_API_ID')), 
                           os.getenv('TG_API_HASH'))
    
    await client.start()
    
    print("🔍 Поиск вакансии ЮК Импульс в job-каналах...\n")
    
    for channel_username in JOB_CHANNELS:
        try:
            print(f"\n📢 Проверяю {channel_username}...")
            channel = await client.get_entity(channel_username)
            
            # Ищем в последних 200 сообщениях
            async for message in client.iter_messages(channel, limit=200):
                if message.text:
                    text_lower = message.text.lower()
                    
                    # Проверяем ключевые слова
                    if any(keyword.lower() in text_lower for keyword in VACANCY_KEYWORDS):
                        print(f"\n✅ НАЙДЕНО!")
                        print(f"   Канал: {channel.title} ({channel_username})")
                        print(f"   Дата: {message.date.strftime('%d.%m.%Y %H:%M')}")
                        print(f"   ID сообщения: {message.id}")
                        print(f"   Ссылка: https://t.me/{channel_username[1:]}/{message.id}")
                        print(f"\n   Текст:")
                        print(f"   {message.text[:500]}...")
                        
                        # Извлекаем контакты
                        import re
                        
                        # Telegram
                        tg_contacts = re.findall(r'@([a-zA-Z0-9_]{5,32})', message.text)
                        if tg_contacts:
                            print(f"\n   📞 Telegram контакты: {', '.join(['@' + c for c in tg_contacts])}")
                        
                        # Email
                        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message.text)
                        if emails:
                            print(f"   📧 Email: {', '.join(emails)}")
                        
                        # Кнопки
                        if message.buttons:
                            print(f"\n   🔘 Кнопки:")
                            for row in message.buttons:
                                for button in row:
                                    print(f"      • {button.text}")
                                    if button.url:
                                        print(f"        {button.url}")
                        
                        print("\n" + "="*60)
                        break
                        
        except Exception as e:
            print(f"   ⚠️ Ошибка: {e}")
            continue
    
    # Дополнительно - поиск через глобальный поиск Telegram
    print("\n\n🌐 Глобальный поиск по Telegram...")
    print("="*60)
    
    try:
        # Поиск по хештегам
        hashtags = ['#AIEngineer', '#LLMEngineer', '#ЮКИмпульс', '#UKImpulse']
        
        for hashtag in hashtags:
            print(f"\n🔍 Поиск по {hashtag}...")
            results = await client.get_messages(None, search=hashtag, limit=20)
            
            for msg in results:
                if msg.text and any(kw.lower() in msg.text.lower() for kw in VACANCY_KEYWORDS):
                    print(f"\n   ✅ Найдено!")
                    print(f"   Дата: {msg.date.strftime('%d.%m.%Y %H:%M')}")
                    print(f"   {msg.text[:200]}...")
                    
    except Exception as e:
        print(f"Ошибка глобального поиска: {e}")
    
    await client.disconnect()
    
    print("\n\n💡 Если вакансия не найдена в Telegram:")
    print("   1. Проверь HH.ru напрямую - там может быть контакт рекрутера")
    print("   2. Возможно, вакансия была удалена или ID канала неверный")
    print("   3. Попробуй поискать 'ЮК Импульс' в Google/Yandex")

if __name__ == '__main__':
    asyncio.run(main())

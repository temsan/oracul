"""
Скрипт для проверки откликов на вакансии через Telegram
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.types import User
import os
from dotenv import load_dotenv

load_dotenv()

# Контакты работодателей из вакансий
EMPLOYERS = {
    'Telegram агрегация': '@mllshkna',
    'Python Developer (боты)': '@s_harli',
    'Telegram mini app': '@kriswerty',
    'Playable Ads': '@Foreverinlovewithsummer',
    'ЮК Импульс': None,  # Через HH
    'МТС Prompt Engineer': None,  # Через HH
    'МТС LLM Engineer': None,  # Через HH
    'Grand Line': None,  # Через HH
    'DevSphere': None,  # Через HH
    'Rubbles': None,  # Через HH
}

# Хештеги для поиска вакансий
HASHTAGS = ['#Удаленка', '#Разработчик']

async def main():
    # Используем существующую сессию
    client = TelegramClient('oracul', 
                           int(os.getenv('TG_API_ID')), 
                           os.getenv('TG_API_HASH'))
    
    await client.start()
    
    print("🔍 Проверка откликов на вакансии...\n")
    
    # Проверяем диалоги с работодателями
    print("📬 Telegram отклики:")
    print("-" * 50)
    
    for job_title, username in EMPLOYERS.items():
        if username:
            try:
                # Получаем диалог с пользователем
                entity = await client.get_entity(username)
                messages = await client.get_messages(entity, limit=10)
                
                # Проверяем есть ли наши сообщения
                our_messages = [msg for msg in messages if msg.out]
                
                if our_messages:
                    last_msg = our_messages[0]
                    print(f"✅ {job_title} ({username})")
                    print(f"   Отправлено: {last_msg.date.strftime('%d.%m.%Y %H:%M')}")
                    print(f"   Текст: {last_msg.text[:100]}...")
                    
                    # Проверяем ответы
                    their_messages = [msg for msg in messages if not msg.out and msg.date > last_msg.date]
                    if their_messages:
                        print(f"   💬 Есть ответ от {their_messages[0].date.strftime('%d.%m.%Y %H:%M')}")
                    else:
                        print(f"   ⏳ Ответа пока нет")
                else:
                    print(f"❌ {job_title} ({username}) - не откликался")
                    
                print()
                
            except Exception as e:
                print(f"⚠️ {job_title} ({username}) - ошибка: {e}\n")
    
    # Проверяем HH вакансии
    print("\n📋 HH.ru вакансии:")
    print("-" * 50)
    for job_title, username in EMPLOYERS.items():
        if username is None:
            print(f"📝 {job_title} - проверь на hh.ru")
    
    # Поиск по хештегам
    print("\n\n🔎 Поиск новых вакансий по хештегам:")
    print("-" * 50)
    
    for hashtag in HASHTAGS:
        try:
            # Поиск по хештегу в последних сообщениях
            results = await client.get_messages(None, search=hashtag, limit=5)
            print(f"\n{hashtag}: найдено {len(results)} сообщений")
            
            for msg in results[:3]:
                if msg.text and len(msg.text) > 50:
                    print(f"  • {msg.date.strftime('%d.%m')}: {msg.text[:100]}...")
                    
        except Exception as e:
            print(f"⚠️ Ошибка поиска по {hashtag}: {e}")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())

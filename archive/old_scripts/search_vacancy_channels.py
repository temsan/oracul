"""
Поиск каналов с вакансиями ЮК Импульс / UK Impulse
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
import os
from dotenv import load_dotenv

load_dotenv()

VACANCY_ID = "129381806"
SEARCH_QUERIES = [
    "ЮК Импульс",
    "UK Impulse",
    "Импульс вакансии",
    "AI Engineer вакансии",
    "129381806"
]

async def main():
    client = TelegramClient('oracul', 
                           int(os.getenv('TG_API_ID')), 
                           os.getenv('TG_API_HASH'))
    
    await client.start()
    
    print("🔍 Поиск каналов и сообщений с вакансией ЮК Импульс...\n")
    
    # Поиск в диалогах
    print("📱 Проверка ваших диалогов...")
    print("-" * 60)
    
    async for dialog in client.iter_dialogs(limit=100):
        if dialog.is_channel or dialog.is_group:
            # Ищем в каждом канале/группе
            try:
                messages = await client.get_messages(dialog.entity, limit=50)
                for msg in messages:
                    if msg.text and (VACANCY_ID in msg.text or 
                                    "импульс" in msg.text.lower() or
                                    "impulse" in msg.text.lower()):
                        print(f"\n✅ Найдено в: {dialog.name}")
                        print(f"   ID: {dialog.entity.id}")
                        if hasattr(dialog.entity, 'username') and dialog.entity.username:
                            print(f"   Username: @{dialog.entity.username}")
                        print(f"   Дата: {msg.date.strftime('%d.%m.%Y %H:%M')}")
                        print(f"   Текст: {msg.text[:200]}...")
                        print(f"   Ссылка: https://t.me/c/{str(dialog.entity.id)[4:]}/{msg.id}")
                        break
            except Exception as e:
                pass
    
    # Глобальный поиск
    print("\n\n🌐 Глобальный поиск...")
    print("-" * 60)
    
    for query in SEARCH_QUERIES:
        print(f"\n🔍 Запрос: '{query}'")
        try:
            result = await client(SearchRequest(
                q=query,
                limit=10
            ))
            
            if result.results:
                print(f"   Найдено результатов: {len(result.results)}")
                for item in result.results[:5]:
                    if hasattr(item, 'username'):
                        print(f"   • @{item.username}")
            else:
                print(f"   Ничего не найдено")
                
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # Поиск по сохраненным сообщениям
    print("\n\n💾 Проверка сохраненных сообщений...")
    print("-" * 60)
    
    try:
        saved_messages = await client.get_messages('me', limit=100)
        for msg in saved_messages:
            if msg.text and (VACANCY_ID in msg.text or 
                            "импульс" in msg.text.lower() or
                            "impulse" in msg.text.lower()):
                print(f"\n✅ Найдено в сохраненных")
                print(f"   Дата: {msg.date.strftime('%d.%m.%Y %H:%M')}")
                print(f"   Текст: {msg.text[:200]}...")
                
                # Если это пересланное сообщение
                if msg.fwd_from:
                    print(f"   Переслано из: {msg.fwd_from}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())

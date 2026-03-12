#!/usr/bin/env python3
"""
Тестирование компонентов Oracul Bot
"""

import asyncio
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.text_analyzer import TextAnalyzer
from analyzers.voice_analyzer import VoiceAnalyzer
from analyzers.channel_analyzer import ChannelAnalyzer
from config.settings import settings


async def test_text_analyzer():
    """Тест анализатора текста"""
    print("🧪 Тестирование анализатора текста...")
    
    analyzer = TextAnalyzer()
    
    test_text = """
    Привет! Сегодня у меня отличное настроение. Я работаю над новым проектом, 
    который может изменить мою жизнь. Немного волнуюсь, но в целом очень рад 
    новым возможностям. Хочу поделиться своими мыслями и получить обратную связь.
    """
    
    try:
        result = await analyzer.analyze(test_text)
        
        if result['success']:
            print("✅ Анализ текста успешен")
            print(f"   Тональность: {result.get('sentiment', {}).get('label', 'N/A')}")
            print(f"   Эмоции: {list(result.get('emotions', {}).keys())}")
            print(f"   Рекомендации: {len(result.get('recommendations', []))}")
        else:
            print(f"❌ Ошибка анализа текста: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Исключение при анализе текста: {e}")


async def test_channel_analyzer():
    """Тест анализатора каналов"""
    print("\n🧪 Тестирование анализатора каналов...")
    
    analyzer = ChannelAnalyzer()
    
    # Пробуем инициализировать (может не получиться без API данных)
    try:
        # Это будет работать только если есть API данные
        api_id = settings.TELEGRAM_API_ID if hasattr(settings, 'TELEGRAM_API_ID') else None
        api_hash = settings.TELEGRAM_API_HASH if hasattr(settings, 'TELEGRAM_API_HASH') else None
        
        if api_id and api_hash:
            success = await analyzer.initialize_client(int(api_id), api_hash)
            if success:
                print("✅ Telethon клиент инициализирован")
                
                # Тестируем на публичном канале
                result = await analyzer.analyze_channel("durov", message_limit=10)
                
                if result['success']:
                    print("✅ Анализ канала успешен")
                    channel_info = result.get('channel_info', {})
                    print(f"   Канал: {channel_info.get('title', 'N/A')}")
                    print(f"   Подписчиков: {channel_info.get('participants_count', 0)}")
                    print(f"   Сообщений проанализировано: {result.get('analyzed_messages', 0)}")
                else:
                    print(f"❌ Ошибка анализа канала: {result.get('error')}")
            else:
                print("❌ Не удалось инициализировать Telethon клиент")
        else:
            print("⚠️ API данные Telegram не настроены, пропускаем тест канала")
            
    except Exception as e:
        print(f"❌ Исключение при анализе канала: {e}")
    finally:
        await analyzer.close()


async def test_settings():
    """Тест настроек"""
    print("\n🧪 Тестирование настроек...")
    
    required_settings = [
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY',
        'DATABASE_URL'
    ]
    
    missing = []
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing.append(setting)
    
    if missing:
        print(f"❌ Отсутствуют настройки: {', '.join(missing)}")
    else:
        print("✅ Все обязательные настройки присутствуют")
    
    # Проверяем дополнительные настройки
    optional_settings = [
        'TELEGRAM_API_ID',
        'TELEGRAM_API_HASH',
        'REDIS_URL'
    ]
    
    for setting in optional_settings:
        if getattr(settings, setting, None):
            print(f"✅ {setting} настроен")
        else:
            print(f"⚠️ {setting} не настроен (опционально)")


async def main():
    """Главная функция тестирования"""
    print("🔮 Тестирование компонентов Oracul Bot\n")
    
    # Тестируем настройки
    await test_settings()
    
    # Тестируем анализатор текста
    await test_text_analyzer()
    
    # Тестируем анализатор каналов
    await test_channel_analyzer()
    
    print("\n🏁 Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main())
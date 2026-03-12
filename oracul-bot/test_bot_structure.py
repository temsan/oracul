#!/usr/bin/env python3
"""
Тестовый запуск для проверки структуры бота
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

# Загружаем переменные окружения
load_dotenv()

def check_environment():
    """Проверка переменных окружения"""
    print("🔧 Проверка переменных окружения:")
    
    required_vars = [
        'BOT_TOKEN',
        'TG_API_ID', 
        'TG_API_HASH',
        'OPENROUTER_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f'YOUR_{var}_HERE':
            print(f"✅ {var}: настроен")
        else:
            print(f"❌ {var}: не настроен")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def check_imports():
    """Проверка импортов"""
    print("\n📦 Проверка импортов:")
    
    try:
        from telethon import TelegramClient
        print("✅ Telethon: OK")
    except ImportError as e:
        print(f"❌ Telethon: {e}")
        return False
    
    try:
        from analyzers.dialog_summary_analyzer import DialogSummaryAnalyzer
        print("✅ DialogSummaryAnalyzer: OK")
    except ImportError as e:
        print(f"❌ DialogSummaryAnalyzer: {e}")
        return False
    
    try:
        from services.openrouter_service import OpenRouterService
        print("✅ OpenRouterService: OK")
    except ImportError as e:
        print(f"❌ OpenRouterService: {e}")
        return False
    
    return True

def main():
    """Основная функция проверки"""
    print("🔮 Тестирование структуры Oracul Bot")
    print("=" * 50)
    
    # Проверяем переменные окружения
    env_ok, missing_vars = check_environment()
    
    # Проверяем импорты
    imports_ok = check_imports()
    
    print("\n" + "=" * 50)
    print("📊 Результат проверки:")
    
    if env_ok and imports_ok:
        print("✅ Все проверки пройдены! Бот готов к запуску.")
        print("\n🚀 Для запуска используйте:")
        print("   python unified_bot.py")
        print("   или")
        print("   python bot_self_analysis.py")
    else:
        print("❌ Обнаружены проблемы:")
        
        if not env_ok:
            print(f"   • Не настроены переменные: {', '.join(missing_vars)}")
            print("   • Отредактируйте файл .env")
        
        if not imports_ok:
            print("   • Проблемы с импортами модулей")
            print("   • Установите зависимости: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
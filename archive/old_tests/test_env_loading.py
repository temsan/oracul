#!/usr/bin/env python3
"""
Тест загрузки переменных окружения
"""

import os
from pathlib import Path
from dotenv import load_dotenv

print("🔍 Тест загрузки переменных окружения")
print("=" * 50)

# Проверяем текущую директорию
print(f"Текущая директория: {os.getcwd()}")

# Проверяем существование .env файла
env_path = Path('.env')
print(f"Путь к .env: {env_path.absolute()}")
print(f"Файл .env существует: {env_path.exists()}")

if env_path.exists():
    print(f"Размер файла: {env_path.stat().st_size} байт")

# Загружаем переменные
print("\n📥 Загрузка переменных...")
load_result = load_dotenv()
print(f"Результат load_dotenv(): {load_result}")

# Проверяем ключевые переменные
variables_to_check = [
    'BOT_TOKEN',
    'OPENROUTER_API_KEY', 
    'DEFAULT_MODEL',
    'TG_API_ID'
]

print("\n🔑 Проверка переменных:")
for var in variables_to_check:
    value = os.getenv(var)
    if value:
        # Показываем только первые символы для безопасности
        display_value = value[:10] + "..." if len(value) > 10 else value
        print(f"✅ {var}: {display_value}")
    else:
        print(f"❌ {var}: НЕ НАЙДЕНА")

print("\n" + "=" * 50)
print("Тест завершен")
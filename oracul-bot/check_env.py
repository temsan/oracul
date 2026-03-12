#!/usr/bin/env python3
"""
Проверка загрузки переменных окружения
"""

import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

print("🔧 Проверка переменных окружения:")
print(f"BOT_TOKEN: {os.getenv('BOT_TOKEN', 'НЕ НАЙДЕН')[:20]}...")
print(f"TG_API_ID: {os.getenv('TG_API_ID', 'НЕ НАЙДЕН')}")
print(f"TG_API_HASH: {os.getenv('TG_API_HASH', 'НЕ НАЙДЕН')[:20]}...")
print(f"OPENROUTER_API_KEY: {os.getenv('OPENROUTER_API_KEY', 'НЕ НАЙДЕН')[:20]}...")

print("\n📁 Проверка файла .env:")
if os.path.exists('.env'):
    print("✅ Файл .env существует")
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"📄 Строк в файле: {len(lines)}")
    
    # Показываем первые несколько строк (без значений)
    for i, line in enumerate(lines[:10]):
        if '=' in line and not line.startswith('#'):
            key = line.split('=')[0]
            print(f"   {key}=...")
else:
    print("❌ Файл .env не найден")
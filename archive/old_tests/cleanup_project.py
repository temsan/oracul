#!/usr/bin/env python3
"""
Скрипт для очистки проекта от дублирующих папок и файлов
"""

import os
import shutil
from pathlib import Path

def analyze_project_structure():
    """Анализ структуры проекта"""
    
    print("🔍 Анализ структуры проекта...")
    
    # Проверяем папки с ботами
    oracul_bot = Path("oracul-bot")
    telegram_bot = Path("telegram-bot")
    
    print(f"\n📁 Папки с ботами:")
    print(f"  oracul-bot/: {'✅ существует' if oracul_bot.exists() else '❌ не найдена'}")
    print(f"  telegram-bot/: {'✅ существует' if telegram_bot.exists() else '❌ не найдена'}")
    
    if oracul_bot.exists():
        oracul_files = list(oracul_bot.rglob("*.py"))
        print(f"    Python файлов: {len(oracul_files)}")
        
        # Основные файлы
        main_files = [
            "bot_self_analysis.py",
            "services/openrouter_service.py", 
            "analyzers/dialog_summary_analyzer.py",
            "prompts.py"
        ]
        
        for file in main_files:
            file_path = oracul_bot / file
            print(f"    {file}: {'✅' if file_path.exists() else '❌'}")
    
    if telegram_bot.exists():
        telegram_files = list(telegram_bot.rglob("*.py"))
        print(f"    Python файлов: {len(telegram_files)}")
        
        # Проверяем основные файлы
        main_files = ["bot.py", "config.py", "api_client.py"]
        for file in main_files:
            file_path = telegram_bot / file
            print(f"    {file}: {'✅' if file_path.exists() else '❌'}")
    
    # Проверяем дублирующие файлы
    print(f"\n🔄 Поиск дублирующих файлов...")
    
    root_py_files = [f for f in Path(".").glob("*.py") if not f.name.startswith("test_")]
    print(f"  Python файлов в корне: {len(root_py_files)}")
    
    for file in root_py_files[:10]:  # Показываем первые 10
        print(f"    {file.name}")
    
    if len(root_py_files) > 10:
        print(f"    ... и еще {len(root_py_files) - 10} файлов")

def get_recommendations():
    """Рекомендации по очистке"""
    
    print(f"\n💡 Рекомендации:")
    
    # Основной бот
    print(f"  1. Основной бот: oracul-bot/ - это главный бот для самоанализа")
    print(f"     ✅ Оставить и развивать")
    
    # Второй бот
    print(f"  2. Второй бот: telegram-bot/ - возможно устаревший")
    print(f"     🤔 Проверить назначение, возможно удалить")
    
    # Файлы в корне
    print(f"  3. Python файлы в корне - много тестовых и экспериментальных")
    print(f"     🧹 Можно перенести в папку scripts/ или удалить неактуальные")
    
    # Промпты
    print(f"  4. Промпты созданы в oracul-bot/prompts.py")
    print(f"     ✅ Централизованное хранение промптов")

def main():
    """Главная функция"""
    print("🧹 Анализ структуры проекта Oracul Bot")
    print("=" * 50)
    
    analyze_project_structure()
    get_recommendations()
    
    print(f"\n📋 Итоги:")
    print(f"  • oracul-bot/ - основной рабочий бот ✅")
    print(f"  • telegram-bot/ - возможно дублирующий бот ❓")
    print(f"  • prompts.py - создан для централизации промптов ✅")
    print(f"  • Много файлов в корне - нужна очистка 🧹")

if __name__ == "__main__":
    main()
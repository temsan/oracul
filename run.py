#!/usr/bin/env python3
"""
Единая точка запуска Oracul Bot.

Запускает:
- Основной бот (unified_bot.py)
- Опционально: Web App для управления сессиями

Usage:
    python run.py              # Запуск только бота
    python run.py --webapp     # Запуск бота и Web App
    python run.py --webapp-only # Запуск только Web App
"""

import argparse
import asyncio
import sys
import subprocess
import os
from pathlib import Path


def run_bot():
    """Запуск основного бота."""
    bot_path = Path(__file__).parent / "oracul-bot" / "unified_bot.py"
    
    print("🚀 Запуск Oracul Bot...")
    print(f"📍 Путь: {bot_path}")
    
    # Запускаем бот как subprocess для корректной работы с async
    try:
        result = subprocess.run(
            [sys.executable, str(bot_path)],
            cwd=str(bot_path.parent),
            check=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка запуска бота: {e}")
        sys.exit(1)


def run_webapp():
    """Запуск Web App для управления сессиями."""
    webapp_path = Path(__file__).parent / "oracul-bot" / "session_webapp.py"
    
    print("🌐 Запуск Web App...")
    print(f"📍 Путь: {webapp_path}")
    print("🔗 URL будет доступен по: http://localhost:8088")
    
    try:
        # Проверяем наличие uvicorn
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uvicorn не установлен. Установите: pip install uvicorn fastapi")
        sys.exit(1)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "uvicorn", "session_webapp:app", 
             "--host", "0.0.0.0", "--port", "8088"],
            cwd=str(webapp_path.parent),
            check=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Web App остановлен")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка запуска Web App: {e}")
        sys.exit(1)


def run_both():
    """Запуск бота и Web App параллельно."""
    import multiprocessing
    
    print("🚀 Запуск Oracul Bot + Web App...")
    print("=" * 50)
    
    # Создаем процессы
    bot_process = multiprocessing.Process(target=run_bot)
    webapp_process = multiprocessing.Process(target=run_webapp)
    
    try:
        # Запускаем оба процесса
        bot_process.start()
        webapp_process.start()
        
        print("✅ Бот и Web App запущены!")
        print("🤖 Bot: работает в Telegram")
        print("🌐 Web App: http://localhost:8088")
        print("=" * 50)
        print("Нажмите Ctrl+C для остановки")
        
        # Ждем завершения
        bot_process.join()
        webapp_process.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Остановка всех сервисов...")
        bot_process.terminate()
        webapp_process.terminate()
        bot_process.join()
        webapp_process.join()
        print("👋 Все сервисы остановлены")


def main():
    parser = argparse.ArgumentParser(
        description="Oracul Bot Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python run.py              # Только бот
  python run.py --webapp     # Бот + Web App
  python run.py --webapp-only # Только Web App
        """
    )
    
    parser.add_argument(
        "--webapp", 
        action="store_true",
        help="Запустить бота и Web App параллельно"
    )
    parser.add_argument(
        "--webapp-only",
        action="store_true", 
        help="Запустить только Web App"
    )
    
    args = parser.parse_args()
    
    # Проверяем наличие .env
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  Внимание: файл .env не найден!")
        print("📋 Скопируйте .env.example в .env и настройте переменные")
        print()
    
    if args.webapp_only:
        run_webapp()
    elif args.webapp:
        run_both()
    else:
        run_bot()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Тестирование Oracul Bot через MCP-подобный интерфейс.
Использует Telethon для взаимодействия с ботом как пользователь.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Добавляем путь к oracul-bot
sys.path.insert(0, str(Path(__file__).parent / "oracul-bot"))

from telethon import TelegramClient
from telethon.tl.custom.message import Message
from dotenv import load_dotenv

# Загружаем env
load_dotenv(Path(__file__).parent / ".env")


class OraculBotTester:
    """Тестер для Oracul Bot через Telegram API"""
    
    def __init__(self):
        self.api_id = int(os.getenv("TG_API_ID", 0))
        self.api_hash = os.getenv("TG_API_HASH", "")
        self.bot_username = "oracul_analysis_bot"  # Укажи username своего бота
        self.session_name = "test_oracul_session"
        self.client = None
        self.test_results = []
        
    async def initialize(self):
        """Инициализация клиента"""
        print("🔄 Инициализация тестового клиента...")
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            print("❌ Требуется авторизация. Войди в Telegram первым запуском:")
            print(f"   python -c \"from telethon import TelegramClient; "
                  f"c = TelegramClient('{self.session_name}', {self.api_id}, '{self.api_hash}'); "
                  f"c.start()\"")
            return False
            
        me = await self.client.get_me()
        print(f"✅ Авторизован как: {me.first_name} (@{me.username})")
        return True
    
    async def send_command(self, command: str) -> Message:
        """Отправка команды боту"""
        print(f"📤 Отправка: {command}")
        message = await self.client.send_message(self.bot_username, command)
        await asyncio.sleep(2)  # Ждем ответ
        return message
    
    async def click_button(self, message: Message, pattern: str) -> Message:
        """Нажатие кнопки по тексту"""
        if not message.buttons:
            print("❌ Нет кнопок в сообщении")
            return None
            
        for row in message.buttons:
            for button in row:
                if pattern.lower() in button.text.lower():
                    print(f"🔘 Нажатие: {button.text}")
                    result = await button.click()
                    await asyncio.sleep(2)
                    return result
                    
        print(f"❌ Кнопка '{pattern}' не найдена")
        return None
    
    async def get_last_message(self) -> Message:
        """Получение последнего сообщения от бота"""
        messages = await self.client.get_messages(self.bot_username, limit=1)
        return messages[0] if messages else None
    
    async def test_start_command(self):
        """Тест команды /start"""
        print("\n📋 Тест: /start")
        await self.send_command("/start")
        msg = await self.get_last_message()
        
        if msg and "Oracul" in msg.text:
            print("✅ /start работает")
            self.test_results.append(("start", True, "OK"))
            return True
        else:
            print("❌ /start не работает")
            self.test_results.append(("start", False, "No response"))
            return False
    
    async def test_help_command(self):
        """Тест команды /help"""
        print("\n📋 Тест: /help")
        await self.send_command("/help")
        msg = await self.get_last_message()
        
        if msg and ("справка" in msg.text.lower() or "help" in msg.text.lower()):
            print("✅ /help работает")
            self.test_results.append(("help", True, "OK"))
            return True
        else:
            print("❌ /help не работает")
            self.test_results.append(("help", False, "No response"))
            return False
    
    async def test_session_button(self):
        """Тест кнопки Сессия"""
        print("\n📋 Тест: Кнопка 'Сессия'")
        
        # Сначала /start
        await self.send_command("/start")
        await asyncio.sleep(1)
        
        # Получаем сообщение с меню
        msg = await self.get_last_message()
        if not msg or not msg.buttons:
            print("❌ Нет меню")
            self.test_results.append(("session_button", False, "No menu"))
            return False
        
        # Ищем и нажимаем кнопку Сессия
        result = await self.click_button(msg, "Сессия")
        if not result:
            self.test_results.append(("session_button", False, "Button not found"))
            return False
        
        # Проверяем ответ
        await asyncio.sleep(1)
        msg = await self.get_last_message()
        
        if msg and ("сессии" in msg.text.lower() or "войти" in msg.text.lower()):
            print("✅ Кнопка 'Сессия' работает")
            self.test_results.append(("session_button", True, "OK"))
            return True
        else:
            print("❌ Кнопка 'Сессия' не работает")
            self.test_results.append(("session_button", False, "Wrong response"))
            return False
    
    async def test_login_flow(self):
        """Тест потока входа (без реального ввода кода)"""
        print("\n📋 Тест: Поток входа")
        
        # Начинаем вход
        await self.send_command("/login")
        await asyncio.sleep(1)
        
        msg = await self.get_last_message()
        if msg and ("вход" in msg.text.lower() or "телефон" in msg.text.lower()):
            print("✅ Поток входа запущен")
            self.test_results.append(("login_flow", True, "OK"))
            return True
        else:
            print("❌ Поток входа не запущен")
            self.test_results.append(("login_flow", False, "No response"))
            return False
    
    async def test_categories_menu(self):
        """Тест меню категорий"""
        print("\n📋 Тест: Меню категорий")
        
        await self.send_command("/start")
        await asyncio.sleep(1)
        
        msg = await self.get_last_message()
        if not msg or not msg.buttons:
            print("❌ Нет меню")
            self.test_results.append(("categories", False, "No menu"))
            return False
        
        # Проверяем наличие категорий
        categories = ["Самоанализ", "Психологический", "Голосовой", "Каналы", "Карьерный", "Ситуации"]
        found = []
        
        for row in msg.buttons:
            for button in row:
                for cat in categories:
                    if cat in button.text:
                        found.append(cat)
        
        if len(found) >= 4:
            print(f"✅ Найдено категорий: {len(found)}")
            self.test_results.append(("categories", True, f"Found {len(found)} categories"))
            return True
        else:
            print(f"❌ Найдено мало категорий: {found}")
            self.test_results.append(("categories", False, f"Only {len(found)} categories"))
            return False
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("=" * 50)
        print("🧪 Oracul Bot MCP Tester")
        print("=" * 50)
        
        if not await self.initialize():
            print("❌ Не удалось инициализировать")
            return
        
        tests = [
            ("start", self.test_start_command),
            ("help", self.test_help_command),
            ("categories", self.test_categories_menu),
            ("session_button", self.test_session_button),
            ("login_flow", self.test_login_flow),
        ]
        
        for name, test_func in tests:
            try:
                await test_func()
            except Exception as e:
                print(f"❌ Ошибка в {name}: {e}")
                self.test_results.append((name, False, str(e)))
        
        # Итоги
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ")
        print("=" * 50)
        
        passed = sum(1 for _, status, _ in self.test_results if status)
        failed = sum(1 for _, status, _ in self.test_results if not status)
        
        for name, status, msg in self.test_results:
            status_str = "✅ PASS" if status else "❌ FAIL"
            print(f"{status_str}: {name} - {msg}")
        
        print(f"\nВсего: {len(self.test_results)} тестов")
        print(f"✅ Пройдено: {passed}")
        print(f"❌ Ошибок: {failed}")
        
        # Отчет в файл
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# Oracul Bot Test Report\n\n")
            f.write(f"Date: {datetime.now().isoformat()}\n\n")
            f.write("| Test | Status | Message |\n")
            f.write("|------|--------|---------|\n")
            for name, status, msg in self.test_results:
                status_mark = "✅" if status else "❌"
                f.write(f"| {name} | {status_mark} | {msg} |\n")
            f.write(f"\n**Total: {len(self.test_results)}, Passed: {passed}, Failed: {failed}**\n")
        
        print(f"\n📝 Отчет сохранен: {report_file}")
    
    async def close(self):
        """Закрытие клиента"""
        if self.client:
            await self.client.disconnect()
            print("👋 Клиент отключен")


async def main():
    tester = OraculBotTester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())

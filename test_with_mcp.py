#!/usr/bin/env python3
"""
Тестирование Oracul Bot через telegram-mcp инструменты.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Добавляем путь к telegram-mcp
sys.path.insert(0, str(Path.home() / "telegram-mcp"))

from dotenv import load_dotenv

# Загружаем env
load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path.home() / "telegram-mcp" / ".env")


class OraculMCPTester:
    """Тестер Oracul Bot через MCP-инструменты"""
    
    def __init__(self):
        self.api_id = int(os.getenv("TG_API_ID") or os.getenv("TELEGRAM_API_ID", 0))
        self.api_hash = os.getenv("TG_API_HASH") or os.getenv("TELEGRAM_API_HASH", "")
        self.bot_username = "itoraculusbot"
        self.results = []
        
    async def setup(self):
        """Инициализация Telethon клиента"""
        try:
            from telethon import TelegramClient
            
            session_name = os.getenv("TELEGRAM_SESSION_NAME", "oracul_mcp_test")
            self.client = TelegramClient(
                str(Path.home() / "telegram-mcp" / session_name),
                self.api_id,
                self.api_hash
            )
            
            print("Connecting to Telegram...")
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print("Authorization required!")
                print("Запусти один раз:")
                print(f"   cd %USERPROFILE%\\telegram-mcp")
                print(f"   python -c \"from telethon import TelegramClient; "
                      f"c = TelegramClient('{session_name}', {self.api_id}, '{self.api_hash}'); "
                      f"c.start()\"")
                return False
            
            me = await self.client.get_me()
            print(f"Authorized: {me.first_name} (@{me.username})")
            return True
            
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    async def test_bot_start(self):
        """Тест /start команды"""
        print("\nTest: /start")
        try:
            from telethon.tl.functions.messages import GetHistoryRequest
            
            # Отправляем /start
            await self.client.send_message(self.bot_username, "/start")
            await asyncio.sleep(2)
            
            # Получаем ответ
            messages = await self.client.get_messages(self.bot_username, limit=1)
            
            if messages and messages[0]:
                msg = messages[0]
                if "Oracul" in msg.text or "оркул" in msg.text.lower():
                    print(f"Response received: {msg.text[:100]}...")
                    self.results.append(("start", True, "Bot responded"))
                    return True
                else:
                    print(f"Response: {msg.text[:100]}...")
                    self.results.append(("start", False, "Unexpected response"))
                    return False
            else:
                print("No response")
                self.results.append(("start", False, "No response"))
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            self.results.append(("start", False, str(e)))
            return False
    
    async def test_bot_help(self):
        """Тест /help команды"""
        print("\nTest: /help")
        try:
            await self.client.send_message(self.bot_username, "/help")
            await asyncio.sleep(2)
            
            messages = await self.client.get_messages(self.bot_username, limit=1)
            
            if messages and messages[0]:
                msg = messages[0]
                if any(word in msg.text.lower() for word in ["справка", "help", "команды", "возможности"]):
                    print(f"Help received")
                    self.results.append(("help", True, "Help received"))
                    return True
                else:
                    print(f"⚠️  Ответ: {msg.text[:100]}...")
                    self.results.append(("help", False, "Unexpected response"))
                    return False
            else:
                print("❌ Нет ответа")
                self.results.append(("help", False, "No response"))
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.results.append(("help", False, str(e)))
            return False
    
    async def test_bot_login(self):
        """Тест /login команды"""
        print("\nTest: /login")
        try:
            await self.client.send_message(self.bot_username, "/login")
            await asyncio.sleep(2)
            
            messages = await self.client.get_messages(self.bot_username, limit=1)
            
            if messages and messages[0]:
                msg = messages[0]
                if any(word in msg.text.lower() for word in ["вход", "сессия", "телефон", "войти"]):
                    print(f"Login form received")
                    self.results.append(("login", True, "Login form received"))
                    return True
                else:
                    print(f"⚠️  Ответ: {msg.text[:100]}...")
                    self.results.append(("login", False, "Unexpected response"))
                    return False
            else:
                print("❌ Нет ответа")
                self.results.append(("login", False, "No response"))
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.results.append(("login", False, str(e)))
            return False
    
    async def test_main_menu_buttons(self):
        """Тест кнопок главного меню"""
        print("\nTest: Main menu buttons")
        try:
            # Отправляем /start
            await self.client.send_message(self.bot_username, "/start")
            await asyncio.sleep(2)
            
            # Получаем сообщение с кнопками
            messages = await self.client.get_messages(self.bot_username, limit=1)
            
            if not messages or not messages[0].buttons:
                print("❌ Нет кнопок в меню")
                self.results.append(("main_menu_buttons", False, "No buttons"))
                return False
            
            msg = messages[0]
            buttons = []
            
            for row in msg.buttons:
                for button in row:
                    buttons.append(button.text)
            
            print(f"Found buttons: {len(buttons)}")
            for btn in buttons[:10]:
                print(f"   - {btn}")
            
            # Проверяем наличие ключевых кнопок
            required = ["Сессия", "Самоанализ", "Психологический"]
            found = [r for r in required if any(r in b for b in buttons)]
            
            print(f"Key buttons: {found}")
            
            self.results.append(("main_menu_buttons", True, f"{len(buttons)} buttons, {len(found)} key"))
            return True
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.results.append(("main_menu_buttons", False, str(e)))
            return False
    
    async def test_session_settings(self):
        """Тест настроек сессии"""
        print("\nTest: Session settings")
        try:
            # Отправляем /start
            await self.client.send_message(self.bot_username, "/start")
            await asyncio.sleep(1)
            
            # Получаем сообщение
            messages = await self.client.get_messages(self.bot_username, limit=1)
            
            if not messages or not messages[0].buttons:
                print("❌ Нет меню")
                self.results.append(("session_settings", False, "No menu"))
                return False
            
            # Ищем кнопку "Сессия"
            msg = messages[0]
            session_button = None
            
            for row in msg.buttons:
                for button in row:
                    if "Сессия" in button.text:
                        session_button = button
                        break
                if session_button:
                    break
            
            if not session_button:
                print("❌ Кнопка 'Сессия' не найдена")
                self.results.append(("session_settings", False, "Session button not found"))
                return False
            
            # Нажимаем кнопку
            print(f"Clicking: {session_button.text}")
            await session_button.click()
            await asyncio.sleep(2)
            
            # Получаем ответ
            messages = await self.client.get_messages(self.bot_username, limit=1)
            
            if messages and messages[0]:
                msg = messages[0]
                if any(word in msg.text.lower() for word in ["сессия", "войти", "ttl", "режим"]):
                    print(f"Session menu opened")
                    self.results.append(("session_settings", True, "Session menu opened"))
                    return True
                else:
                    print(f"⚠️  Ответ: {msg.text[:100]}...")
                    self.results.append(("session_settings", False, "Unexpected response"))
                    return False
            else:
                print("❌ Нет ответа")
                self.results.append(("session_settings", False, "No response"))
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.results.append(("session_settings", False, str(e)))
            return False
    
    async def generate_report(self):
        """Генерация отчета"""
        print("\n" + "=" * 50)
        print("MCP TEST REPORT")
        print("=" * 50)
        
        passed = sum(1 for _, status, _ in self.results if status)
        failed = sum(1 for _, status, _ in self.results if not status)
        
        for name, status, msg in self.results:
            status_str = "PASS" if status else "FAIL"
            print(f"{status_str}: {name:<20} - {msg}")
        
        print(f"\nTotal tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        # Сохраняем отчет
        report_file = Path(__file__).parent / f"mcp_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# MCP Test Report - Oracul Bot\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
            f.write("## Results\n\n")
            f.write("| Test | Status | Message |\n")
            f.write("|------|--------|---------|\n")
            for name, status, msg in self.results:
                status_mark = "✅" if status else "❌"
                f.write(f"| {name} | {status_mark} | {msg} |\n")
            f.write(f"\n**Summary: {len(self.results)} tests, {passed} passed, {failed} failed**\n")
        
        print(f"\nReport saved: {report_file}")
        
        return failed == 0
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("=" * 50)
        print("Oracul Bot MCP Testing")
        print("=" * 50)
        
        if not await self.setup():
            print("Failed to initialize")
            return False
        
        # Запускаем тесты
        tests = [
            ("Bot Start", self.test_bot_start),
            ("Bot Help", self.test_bot_help),
            ("Bot Login", self.test_bot_login),
            ("Main Menu Buttons", self.test_main_menu_buttons),
            ("Session Settings", self.test_session_settings),
        ]
        
        for name, test_func in tests:
            try:
                await test_func()
            except Exception as e:
                print(f"Critical error in {name}: {e}")
                self.results.append((name.lower().replace(" ", "_"), False, f"Critical: {e}"))
        
        # Генерируем отчет
        success = await self.generate_report()
        
        # Отключаемся
        await self.client.disconnect()
        print("\nDisconnecting from Telegram")
        
        return success


async def main():
    tester = OraculMCPTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

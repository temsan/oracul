#!/usr/bin/env python3
"""
Демо MCP тестирования без реальных запросов к Telegram.
Показывает структуру и возможности MCP.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("MCP Testing Demo - Oracul Bot")
print("=" * 60)

# Проверяем MCP сервер
sys.path.insert(0, str(Path.home() / "telegram-mcp"))

try:
    from telethon import TelegramClient
    print("\n[OK] Telethon imported")
except ImportError as e:
    print(f"\n[FAIL] Telethon: {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("[OK] python-dotenv imported")
except ImportError as e:
    print(f"[FAIL] python-dotenv: {e}")
    sys.exit(1)

# Проверяем конфигурацию
print("\n[Configuration]")
mcp_env = Path.home() / "telegram-mcp" / ".env"
if mcp_env.exists():
    with open(mcp_env) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0]
                print(f"  - {key}: configured")

# Проверяем сессии
print("\n[Session Files]")
session_files = [
    Path.home() / "telegram-mcp" / "oracul_test_session.session",
    Path.home() / "telegram-mcp" / "telegram_session.session",
    Path(__file__).parent / "bot_session.session",
    Path(__file__).parent / "oracul.session",
]

for sf in session_files:
    if sf.exists():
        print(f"  - {sf.name}: {sf.stat().st_size} bytes")

# MCP Tools
print("\n[MCP Tools Available]")
tools = [
    ("get_chats", "Get list of chats"),
    ("list_chats", "List chats with metadata"),
    ("send_message", "Send message to chat"),
    ("get_messages", "Get messages from chat"),
    ("get_me", "Get current user info"),
    ("list_contacts", "List contacts"),
    ("search_public_chats", "Search public chats"),
]

for tool, desc in tools:
    print(f"  - {tool}: {desc}")

# Тестовые сценарии
print("\n[Test Scenarios]")
scenarios = [
    "1. Send /start to @itoraculusbot",
    "2. Check response contains menu",
    "3. Click 'Session' button",
    "4. Verify session settings menu",
    "5. Send /login command",
    "6. Verify login flow started",
]

for scenario in scenarios:
    print(f"  {scenario}")

# Проверяем Oracul Bot
print("\n[Oracul Bot Check]")
sys.path.insert(0, str(Path(__file__).parent / "oracul-bot"))

try:
    from unified_bot import UnifiedOracul
    bot = UnifiedOracul()
    print(f"  - Bot initialized: OK")
    print(f"  - Categories: {len(bot.analysis_categories)}")
    print(f"  - Session TTL: {bot.default_session_ttl_minutes} min")
    print(f"  - Session methods: {len([m for m in dir(bot) if 'session' in m])}")
except Exception as e:
    print(f"  - Bot check failed: {e}")

print("\n" + "=" * 60)
print("MCP Demo Complete!")
print("=" * 60)
print("\nTo run real tests:")
print("1. Create user session (not bot):")
print("   cd %USERPROFILE%\\telegram-mcp")
print("   python session_string_generator.py")
print("\n2. Run tests:")
print("   python test_with_mcp.py")
print("\nOr use MCP server directly:")
print("   python %USERPROFILE%\\telegram-mcp\\main.py")

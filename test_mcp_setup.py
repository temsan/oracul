#!/usr/bin/env python3
"""
Проверка установки и настройки telegram-mcp.
Демонстрация работы с MCP инструментами.
"""

import sys
import os
from pathlib import Path

# Добавляем путь к telegram-mcp
sys.path.insert(0, str(Path.home() / "telegram-mcp"))

print("=" * 60)
print("Telegram MCP Setup Verification")
print("=" * 60)

# Проверка 1: Импорты
print("\n[1] Checking imports...")
try:
    from telethon import TelegramClient
    print("  - Telethon: OK")
except ImportError as e:
    print(f"  - Telethon: FAIL - {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("  - python-dotenv: OK")
except ImportError as e:
    print(f"  - python-dotenv: FAIL - {e}")
    sys.exit(1)

try:
    from mcp import ClientSession
    print("  - MCP SDK: OK")
except ImportError as e:
    print(f"  - MCP SDK: FAIL - {e}")
    sys.exit(1)

print("\n[2] Checking environment...")
# Загружаем env
env_path = Path.home() / "telegram-mcp" / ".env"
if env_path.exists():
    print(f"  - MCP .env exists: {env_path}")
    with open(env_path) as f:
        content = f.read()
        if "TELEGRAM_API_ID" in content:
            print("  - TELEGRAM_API_ID: configured")
        if "TELEGRAM_API_HASH" in content:
            print("  - TELEGRAM_API_HASH: configured")
else:
    print(f"  - MCP .env: NOT FOUND")

oracul_env = Path(__file__).parent / ".env"
if oracul_env.exists():
    print(f"  - Oracul .env exists: {oracul_env}")

print("\n[3] Checking MCP server files...")
mcp_path = Path.home() / "telegram-mcp"
files_to_check = [
    "main.py",
    "requirements.txt",
    ".env",
]

for file in files_to_check:
    filepath = mcp_path / file
    if filepath.exists():
        print(f"  - {file}: OK")
    else:
        print(f"  - {file}: MISSING")

print("\n[4] Available MCP Tools (from telegram-mcp):")
tools = [
    "get_chats",
    "list_chats", 
    "send_message",
    "get_messages",
    "list_contacts",
    "search_public_chats",
    "get_me",
    "get_user_status",
]

for tool in tools:
    print(f"  - {tool}")

print("\n[5] Session files:")
session_files = list(Path.home().glob("*.session"))
session_files.extend(Path.home().glob("telegram-mcp/*.session"))
session_files.extend(Path(__file__).parent.glob("*.session"))

if session_files:
    for sf in set(str(f) for f in session_files):
        print(f"  - {sf}")
else:
    print("  No session files found")
    print("  To create a session, run:")
    print("    cd %USERPROFILE%\\telegram-mcp")
    print("    python session_string_generator.py")

print("\n" + "=" * 60)
print("MCP Setup Verification Complete!")
print("=" * 60)
print("\nTo test Oracul Bot with MCP:")
print("1. Ensure you have a Telegram session (see above)")
print("2. Run: python test_with_mcp.py")
print("\nOr use the telegram-mcp server directly:")
print("  cd %USERPROFILE%\\telegram-mcp")
print("  python main.py")

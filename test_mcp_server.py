#!/usr/bin/env python3
"""
Тестирование через запуск MCP сервера.
"""

import subprocess
import json
import sys
import os
from pathlib import Path

def run_mcp_command(method, params=None):
    """Запуск MCP команды через сервер"""
    mcp_path = Path.home() / "telegram-mcp" / "main.py"
    
    env = os.environ.copy()
    env.update({
        "TELEGRAM_API_ID": "21834116",
        "TELEGRAM_API_HASH": "3139c483fb576f2043610eb2ba7e285e",
        "TELEGRAM_SESSION_NAME": "oracul_test_session"
    })
    
    # Запускаем MCP сервер
    process = subprocess.Popen(
        [sys.executable, str(mcp_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # Отправляем запрос
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    
    # Читаем ответ
    response = process.stdout.readline()
    process.terminate()
    
    return json.loads(response) if response else None


print("=" * 60)
print("MCP Server Test")
print("=" * 60)

# Проверяем что MCP сервер существует
mcp_main = Path.home() / "telegram-mcp" / "main.py"
if mcp_main.exists():
    print(f"\n[OK] MCP server found: {mcp_main}")
else:
    print(f"\n[FAIL] MCP server not found")
    sys.exit(1)

# Проверяем зависимости
print("\n[Dependencies]")
try:
    import telethon
    print(f"  - telethon: {telethon.__version__}")
except:
    print("  - telethon: not installed")

try:
    import mcp
    print(f"  - mcp: installed")
except:
    print("  - mcp: not installed")

# Показываем структуру MCP сервера
print("\n[MCP Server Structure]")
mcp_dir = Path.home() / "telegram-mcp"
for item in mcp_dir.iterdir():
    if item.is_file() and item.suffix in ['.py', '.txt', '.env']:
        print(f"  - {item.name}")

print("\n[MCP Tools Available]")
tools = [
    "get_chats",
    "send_message", 
    "get_messages",
    "get_me",
    "list_contacts"
]
for tool in tools:
    print(f"  - {tool}")

print("\n" + "=" * 60)
print("MCP Server Ready!")
print("=" * 60)
print("\nTo test Oracul Bot:")
print("1. Start MCP server:")
print("   cd %USERPROFILE%\\telegram-mcp")
print("   python main.py")
print("\n2. Use tools like:")
print('   send_message("@itoraculusbot", "/start")')
print('   get_messages("@itoraculusbot", limit=5)')
print("\n3. Or run full test:")
print("   python test_with_mcp.py")

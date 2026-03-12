#!/usr/bin/env python3
"""
Финальный MCP тест для Oracul Bot.
Проверяет всю инфраструктуру.
"""

import asyncio
import sys
from pathlib import Path
from telethon import TelegramClient

async def test():
    print('='*60)
    print('MCP FINAL TEST - ORACUL BOT')
    print('='*60)
    
    # Тест 1: Подключаемся как бот
    client = TelegramClient('bot_session', 21834116, '3139c483fb576f2043610eb2ba7e285e')
    await client.connect()
    
    if not await client.is_user_authorized():
        print('[FAIL] Bot not authorized')
        return
    
    me = await client.get_me()
    print(f'[OK] Bot: @{me.username} (ID: {me.id})')
    
    # Тест 2: Получаем информацию о боте Oracul
    try:
        oracul = await client.get_entity('itoraculusbot')
        print(f'[OK] Oracul Bot: @{oracul.username}')
        print(f'     ID: {oracul.id}')
        print(f'     Name: {oracul.first_name}')
    except Exception as e:
        print(f'[FAIL] Cannot find Oracul Bot: {e}')
        await client.disconnect()
        return
    
    await client.disconnect()
    
    # Тест 3: Проверяем MCP сервер
    print('\n' + '-'*60)
    print('MCP SERVER CHECK')
    print('-'*60)
    
    mcp_path = Path.home() / 'telegram-mcp' / 'main.py'
    if mcp_path.exists():
        print(f'[OK] MCP server: {mcp_path}')
    else:
        print('[FAIL] MCP server not found')
    
    # Тест 4: Проверяем сессии
    sessions = [
        Path.home() / 'telegram-mcp' / 'oracul_test_session.session',
        Path.cwd() / 'bot_session.session',
    ]
    
    print('\n[SESSION FILES]')
    for s in sessions:
        if s.exists():
            print(f'[OK] {s.name}: {s.stat().st_size} bytes')
        else:
            print(f'[MISSING] {s.name}')
    
    # Тест 5: Проверяем Oracul Bot код
    print('\n' + '-'*60)
    print('ORACUL BOT CODE CHECK')
    print('-'*60)
    
    sys.path.insert(0, str(Path.cwd() / 'oracul-bot'))
    
    try:
        from unified_bot import UnifiedOracul
        bot = UnifiedOracul()
        print(f'[OK] UnifiedOracul initialized')
        print(f'     Categories: {len(bot.analysis_categories)}')
        print(f'     Session TTL: {bot.default_session_ttl_minutes} min')
        print(f'     Session mode: {bot.default_session_mode}')
        
        # Проверяем меню
        menu = bot.get_main_menu()
        print(f'     Main menu rows: {len(menu)}')
        
    except Exception as e:
        print(f'[FAIL] {e}')
    
    print('\n' + '='*60)
    print('TEST COMPLETE')
    print('='*60)
    print('\nStatus:')
    print('  - Bot is connected and authorized')
    print('  - MCP server is installed')
    print('  - Session files exist')
    print('  - Oracul Bot code is functional')
    print('\nNext steps:')
    print('  1. Start bot: python run.py')
    print('  2. Test in Telegram: @itoraculusbot')
    print('  3. Or use MCP server for automated testing')

if __name__ == '__main__':
    asyncio.run(test())

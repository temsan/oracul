# MCP Тестирование Oracul Bot

## Установка MCP сервера

### 1. Клонирование репозитория

```bash
cd %USERPROFILE%
git clone https://github.com/chigwell/telegram-mcp.git
cd telegram-mcp
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

**Зависимости:**
- telethon>=1.39.0
- mcp[cli]>=1.4.1
- python-dotenv>=1.1.0
- httpx>=0.28.1

### 3. Настройка окружения

Создай файл `.env` в папке `telegram-mcp`:

```env
TELEGRAM_API_ID=21834116
TELEGRAM_API_HASH=3139c483fb576f2043610eb2ba7e285e
TELEGRAM_SESSION_NAME=oracul_test_session
```

### 4. Создание сессии

**Вариант A: Интерактивная авторизация**

```bash
cd %USERPROFILE%\telegram-mcp
python session_string_generator.py
```

Введи номер телефона и код из Telegram.

**Вариант B: Через Telethon напрямую**

```python
from telethon import TelegramClient

async def main():
    client = TelegramClient('oracul_test_session', 21834116, '3139c483fb576f2043610eb2ba7e285e')
    await client.start()
    print("Authorized!")
    await client.disconnect()

import asyncio
asyncio.run(main())
```

## Запуск MCP сервера

```bash
cd %USERPROFILE%\telegram-mcp
python main.py
```

Сервер запустит STDIO транспорт для MCP.

## Доступные MCP инструменты

### Чаты
- `get_chats(page, page_size)` - список чатов
- `list_chats(chat_type, limit)` - чаты с фильтрацией
- `get_chat(chat_id)` - информация о чате

### Сообщения
- `send_message(chat_id, message)` - отправить сообщение
- `get_messages(chat_id, page, page_size)` - получить сообщения
- `reply_to_message(chat_id, message_id, text)` - ответить

### Пользователи
- `get_me()` - информация о текущем пользователе
- `list_contacts()` - список контактов
- `get_user_status(user_id)` - статус пользователя

## Тестирование Oracul Bot

### Автоматический тест

```bash
cd C:\Users\temsan\IdeaProjects\Oracul
python test_with_mcp.py
```

### Проверка настройки

```bash
python test_mcp_setup.py
```

### Ручное тестирование через MCP

1. Запусти MCP сервер:
   ```bash
   cd %USERPROFILE%\telegram-mcp
   python main.py
   ```

2. Используй инструменты для тестирования:
   ```python
   # Отправить /start боту
   send_message("@oracul_analysis_bot", "/start")
   
   # Получить ответ
   get_messages("@oracul_analysis_bot", limit=1)
   
   # Отправить /login
   send_message("@oracul_analysis_bot", "/login")
   ```

## Интеграция с Claude Desktop

Добавь в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "python",
      "args": [
        "C:\\Users\\%USERNAME%\\telegram-mcp\\main.py"
      ],
      "env": {
        "TELEGRAM_API_ID": "21834116",
        "TELEGRAM_API_HASH": "3139c483fb576f2043610eb2ba7e285e",
        "TELEGRAM_SESSION_NAME": "oracul_test_session"
      }
    }
  }
}
```

## Тестовые сценарии

### Сценарий 1: Проверка старта

1. Отправить `/start`
2. Проверить наличие меню с 6 категориями
3. Проверить кнопку "Сессия"

### Сценарий 2: Тест сессий

1. Нажать "Сессия"
2. Проверить наличие кнопок:
   - Войти
   - TTL режимы
   - Настройки

### Сценарий 3: Тест категорий

1. Нажать "Самоанализ диалогов"
2. Проверить меню анализа
3. Проверить кнопку "Мои чаты"

## Отладка

### Проверка сессии

```bash
python -c "
from telethon import TelegramClient
client = TelegramClient('oracul_test_session', 21834116, '3139c483fb576f2043610eb2ba7e285e')
client.connect()
print('Authorized:', client.is_user_authorized())
client.disconnect()
"
```

### Логи MCP сервера

```bash
cd %USERPROFILE%\telegram-mcp
python main.py 2>&1 | tee mcp.log
```

## Структура проекта

```
telegram-mcp/
├── main.py              # MCP сервер
├── session_string_generator.py
├── requirements.txt
├── .env
└── oracul_test_session.session  # Файл сессии

Oracul/
├── test_with_mcp.py     # Автоматические тесты
├── test_mcp_setup.py    # Проверка настройки
├── MCP_TESTING.md       # Эта документация
└── ...
```

## Полезные ссылки

- [telegram-mcp GitHub](https://github.com/chigwell/telegram-mcp)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Telethon Documentation](https://docs.telethon.dev/)

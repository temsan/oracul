# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Язык общения

Всегда отвечай на русском. Коммиты пишутся на русском.

## Описание проекта

Oracul Bot — Telegram-бот для самоанализа диалогов с AI. Анализирует текст, голос и изображения через мультимодальные анализаторы. Использует LLM-модели через OpenRouter API с автоматическим fallback при rate limits (каскад из 4 моделей).

## Команды

```bash
# Запуск через единую точку входа
python run.py              # Только бот
python run.py --webapp     # Бот + Web App
python run.py --webapp-only # Только Web App

# Или напрямую:
cd oracul-bot && python unified_bot.py

# Установка зависимостей (из корня проекта)
pip install -r requirements.txt

# Тесты (автономные скрипты, НЕ pytest)
cd oracul-bot && python test_analyzers_only.py   # анализаторы (asyncio)
cd oracul-bot && python test_bot.py               # бот
cd oracul-bot && python test_bot_structure.py      # структура
cd oracul-bot && python test_voice_analyzer.py     # голосовой анализ

# Линтинг и форматирование
cd oracul-bot && black .
cd oracul-bot && isort .
cd oracul-bot && flake8
cd oracul-bot && mypy .

# Docker (контекст сборки — КОРЕНЬ репозитория)
docker build -t oracul-bot -f oracul-bot/Dockerfile .
docker run -it --env-file .env oracul-bot
```

## Архитектура

Весь рабочий код — в `oracul-bot/`.

### Точка входа: `oracul-bot/unified_bot.py` (~420 строк)

Класс `UnifiedOracul` наследует 4 миксина из `bot/`:
- `MenuMixin` — генерация кнопочных меню
- `ChatHandlerMixin` — листинг чатов, сбор и фильтрация сообщений
- `AnalysisHandlerMixin` — обработчики анализов (психологический, голосовой, карьерный)
- `FormatterMixin` — форматирование и отправка результатов

В самом `unified_bot.py` остаётся: `__init__`, `initialize`, `run`, `handle_start`, `handle_help`, `handle_category_selection`, `_route_callback`.

### Модули бота (`oracul-bot/bot/`)

```
bot/
├── __init__.py              # Экспорт миксинов
├── menus.py                 # MenuMixin: get_main_menu, get_*_menu (~90 строк)
├── chat_handlers.py         # ChatHandlerMixin: листинг чатов, сбор сообщений (~370 строк)
├── analysis_handlers.py     # AnalysisHandlerMixin: все handle_* для анализов (~460 строк)
└── formatters.py            # FormatterMixin: send_analysis_result, get_analysis_type_name (~90 строк)
```

### Ключевые паттерны

- **Миксины** — логика разбита по модулям, все методы используют `self.*` от основного класса
- **Система сессий пользователей:** Каждый пользователь бота авторизуется отдельно через свой Telegram-аккаунт. Поддерживаются режимы:
  - `persistent` (TTL) — сессия с ограниченным временем жизни, автоматически продлевается при активности
  - `temporary` — одноразовая сессия, автоматически удаляется после каждого запроса
- **Хранение сессий:** JSON-файл `data/user_auth_sessions.json` с StringSession от Telethon
- **Web App:** FastAPI-приложение `session_webapp.py` для управления сессиями через веб-интерфейс
- **Маршрутизация callback-кнопок** — метод `_route_callback` в `unified_bot.py`
- **Состояния пользователей:** `self.user_states: dict` (ключ: `user_id`, значение: dict с `state`, `analysis_type`, `limit`)
- **Async/await повсюду** — telethon + aiohttp + asyncio

### Сервисы (`oracul-bot/services/`)

- **`openrouter_service.py`** — каскад 4 моделей с автоматическим fallback при HTTP 429. Переиспользует `aiohttp.ClientSession` через `_get_session()`. Закрытие через `close()`
- **`analysis_service.py`** — оркестрация через `TextAnalyzer`/`VoiceAnalyzer` (OpenAI API)
- **`channel_service.py`** — анализ Telegram-каналов через Telethon
- **`user_service.py`** — управление пользователями, лимиты, кэширование через Redis

### Анализаторы (`oracul-bot/analyzers/`)

Активный анализатор: `dialog_summary_analyzer_simple.py` → `DialogSummaryAnalyzer`:
1. Статистика сообщений (text/voice counts)
2. Если текст > 50 символов: отправка в OpenRouter через `_analyze_dialog_text()`
3. Fallback при ошибке OpenRouter: keyword-анализ через словарь из 10 тем

### Промпты (`oracul-bot/prompts.py`)

- Класс `AnalysisPrompts` — промпты для анализа диалогов, текста, голоса (JSON-формат ответов)
- Класс `SystemPrompts` — системные роли: `DIALOG_ANALYST`, `VOICE_ANALYST`, `PERSONALITY_ANALYST`

### БД и модели

- **`models/database.py`** — SQLAlchemy 2.0: `User`, `Analysis`, `Insight`, `UserSession`, `Analytics`
- **`database/connection.py`** — async engine (asyncpg/aiosqlite), `CacheManager` (Redis опционален, обёрнут в try/except)
- **`config/settings.py`** — Pydantic BaseSettings, `get_settings()` возвращает None при ошибке
- **`alembic/`** — миграции БД

### Поток данных

`Telegram event` → `unified_bot.py (_route_callback)` → `bot/*.py (handlers)` → `DialogSummaryAnalyzer` → `OpenRouterService` → ответ пользователю

### Сессии пользователей

**Авторизация:**
- Кнопка «🔐 Сессия» в главном меню или команда `/login`
- Пользователь вводит номер телефона → получает код в Telegram → вводит код → сессия активна
- Поддержка 2FA (двухфакторной аутентификации)

**Управление:**
- Кнопки выбора TTL (15 мин - 1 день)
- Режимы: TTL (постоянная с продлением) или Временный чат (одноразовая)
- Команда `/logout` для выхода
- Web App для расширенного управления (если настроен `SESSION_WEB_APP_URL`)

## Конфигурация

`.env` в корне проекта (не в `oracul-bot/`):
- `BOT_TOKEN` — токен Telegram бота
- `TG_API_ID`, `TG_API_HASH` — Telegram API credentials
- `OPENROUTER_API_KEY` — ключ OpenRouter для LLM
- `DEFAULT_MODEL`, `BACKUP_MODEL`, `THIRD_MODEL`, `FOURTH_MODEL` — каскад моделей

БД по умолчанию: SQLite (`sqlite+aiosqlite:///./tg_analysis.db`), поддерживается PostgreSQL.

## Правила кодирования

- Не создавать файлы в корне — распределять по модулям в `oracul-bot/`
- Файлы до 200-300 строк, иначе рефакторить
- Не перезаписывать `.env` без подтверждения
- Mock-данные только в тестах
- При исправлении ошибок сначала использовать существующие паттерны
- Удалять старую реализацию после замены
- Не хранить кэши в проекте (.mypy_cache, __pycache__)

# Технологический стек и система сборки

## Основные технологии

### Backend и API
- **Python 3.9+** с FastAPI для высокопроизводительных async API
- **PostgreSQL 15** для структурированного хранения данных
- **Redis 7** для кеширования и управления сессиями
- **SQLAlchemy 2.0** с async поддержкой для ORM
- **Alembic** для миграций базы данных

### AI и машинное обучение
- **OpenRouter API** для доступа к современным LLM (GPT-5.2, Claude 4.5, Gemini 3 Pro)
- **Transformers** библиотека для локального инференса моделей
- **PyTorch** для глубокого обучения (оптимизирован для RTX 2050 с CUDA)
- **LangChain** для оркестрации AI-воркфлоу
- **Sentence Transformers** для эмбеддингов
- **Whisper** для транскрипции голоса
- **Современные модели 2026**: GPT-5.2 Pro, Claude Opus 4.5, Gemini 3 Flash, DeepSeek V3.2, Qwen3 Max, GLM-4.7, ByteDance Seed 1.6

### Интеграция с Telegram
- **Telethon** для операций с Telegram API клиентом
- **aiogram 3.x** для разработки ботов
- **python-telegram-bot** для продвинутых функций ботов

### Обработка данных
- **Pandas & NumPy** для манипуляции данными
- **NLTK & spaCy** для NLP предобработки
- **librosa** для анализа аудио
- **Pillow** для обработки изображений

## Команды сборки и разработки

### Настройка окружения
```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env с вашими API ключами

# Настройка базы данных
alembic upgrade head
```

### Разработка
```bash
# Запуск backend API
cd backend && python app/main.py
# или
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Запуск основного бота Оракул
cd oracul-bot && python bot_self_analysis.py

# Запуск устаревшего telegram-bot (не рекомендуется)
cd telegram-bot && python bot.py
```

### Docker развертывание
```bash
# Полное развертывание стека
docker-compose up -d

# Локальная разработка с внешними сервисами
docker-compose -f docker-compose-local.yml up -d

# Сборка конкретного сервиса
docker-compose build oracul-bot
```

### Тестирование и качество кода
```bash
# Запуск тестов
pytest

# Форматирование кода
black .
isort .

# Линтинг
flake8
mypy .

# Тестирование конкретных компонентов
python scripts/test_oracul.py
python oracul-bot/test_analyzers_only.py
```

### Сбор данных и анализ
```bash
# Сбор данных Telegram
python scripts/telegram_data_collection/collect_and_analyze.py

# Анализ пользователей
python scripts/user_analysis/multimodal_analyzer.py

# Анализ каналов
python scripts/channel_analysis/channel_summary.py

# Поиск карьерных возможностей
python scripts/career_job_search/get_job_market_post.py
```

## Управление конфигурацией

### Переменные окружения
- **API ключи**: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `OPENROUTER_API_KEY`
- **База данных**: `DATABASE_URL`, `REDIS_URL`
- **Модели**: `DEFAULT_MODEL`, `BACKUP_MODEL`
- **Отладка**: `DEBUG`, `LOG_LEVEL`

### Конфигурация моделей
- **Флагманская**: `openai/gpt-5.2-pro` (глубокое мышление, 400K контекст)
- **Универсальная**: `openai/gpt-5.2` (адаптивное мышление, 400K контекст)
- **Кодинг**: `anthropic/claude-opus-4.5` (агентные задачи, инженерия)
- **Быстрая**: `google/gemini-3-flash-preview` (скорость + мышление, 1M контекст)
- **Мультимодальная**: `bytedance/seed-1.6` (текст + видео + изображения, 256K)
- **Экономичная**: `deepseek/v3.2` (качество GPT-4o за 1/40 цены)
- **Локальные**: Qwen3 32B, GLM-4.7, NVIDIA Nemotron 3 Nano (оптимизированы для RTX 2050)

## Соображения производительности

- **Поддержка CUDA**: Оптимизировано для RTX 2050 с эффективным использованием памяти
- **Ограничение скорости**: Автоматическое переключение между API провайдерами
- **Кеширование**: Redis для кеширования сессий и результатов анализа
- **Асинхронная обработка**: Полный паттерн async/await для I/O операций
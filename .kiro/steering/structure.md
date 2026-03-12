# Структура проекта и организация

## Корневая структура директорий

```
oracul-bot-repo/
├── oracul-bot/                # Основной бот Оракул (самоанализ)
├── archive/                   # Устаревший код и эксперименты
├── docs/                      # Документация
├── downloads/                 # Временные загрузки
├── .kiro/                     # Конфигурация Kiro IDE
└── oracul-analysis-engine/    # Отдельный проект анализов (независимый)
```

## Структура основного приложения

### Oracul Bot (`oracul-bot/`) - ОСНОВНОЙ
Бот для самоанализа с модульной архитектурой:
```
oracul-bot/
├── unified_bot.py         # Объединенный бот (MAIN ENTRY POINT)
├── bot_self_analysis.py   # Оригинальный бот самоанализа
├── analyzers/             # Движки анализа (текст, голос, мультимодальный)
├── bot/                   # Обработчики бота и команды
├── models/                # Модели данных
├── services/              # Бизнес-логика
├── database/              # Утилиты базы данных
├── config/                # Управление конфигурацией
└── prompts.py             # AI промпты
```

## Отдельный проект анализов

### Analysis Engine (`oracul-analysis-engine/`) - НЕЗАВИСИМЫЙ
Коллекция скриптов для анализа каналов и карьерных возможностей:
```
oracul-analysis-engine/
├── analysis/              # Результаты анализа и отчеты
├── scripts/               # Утилитарные скрипты по функциям
├── CLIProxyAPIPlus/       # API прокси для доступа к LLM
├── docker-compose.yml     # Развертывание (опционально)
├── requirements.txt       # Зависимости
├── run_analysis.py        # Точка входа
├── .env                   # Конфигурация
├── oracul.session         # Telegram сессия
└── README.md              # Документация
```

### Организация скриптов анализов (`oracul-analysis-engine/scripts/`)
Организованы по функциональным доменам:
```
scripts/
├── telegram_data_collection/ # Сбор данных через Telegram API
├── user_analysis/           # Психологическое профилирование
├── channel_analysis/        # Анализ контента каналов
├── career_job_search/       # Анализ рынка труда
├── system_setup/           # Конфигурация окружения
└── modules/                # Переиспользуемые компоненты
```

### Результаты анализа (`oracul-analysis-engine/analysis/`)
```
analysis/
├── user_profiles/          # Анализы отдельных пользователей
├── career_development/     # Материалы по карьере
├── channel_research/       # Отчеты анализа каналов
├── raw_data/              # Исходные файлы данных
└── competitive_analysis/   # Исследования рынка
```

## Паттерны конфигурации

### Конфигурация окружения
- **Oracul Bot**: `.env` в `oracul-bot/`
- **Analysis Engine**: `.env` в `oracul-analysis-engine/`
- Независимые конфигурации для каждого проекта

### Структура логирования
- **Oracul Bot**: Логи в `oracul-bot/logs/`
- **Analysis Engine**: Логи в `oracul-analysis-engine/logs/`
- Структурированное логирование с correlation ID

## Рабочий процесс разработки

### Разработка Oracul Bot
1. Работать в директории `oracul-bot/`
2. Основной файл: `unified_bot.py`
3. Добавлять анализаторы в `analyzers/`
4. Тестировать с `test_*.py` файлами

### Разработка Analysis Engine
1. Работать в директории `oracul-analysis-engine/`
2. Добавлять скрипты в соответствующие поддиректории `scripts/`
3. Результаты сохранять в `analysis/`
4. Использовать Docker для развертывания

### Паттерн потока данных

#### Oracul Bot:
```
Telegram API → Bot Handlers → Analyzers → User Response
```

#### Analysis Engine:
```
Telegram API → Scripts → Analysis Results → Storage
```

### Соглашения именования файлов
- **Скрипты**: `глагол_существительное.py` (например, `analyze_user.py`, `collect_messages.py`)
- **Анализаторы**: `[тип]_analyzer.py` (например, `text_analyzer.py`, `voice_analyzer.py`)
- **Модели**: `[сущность].py` (например, `user.py`, `message.py`)
- **Результаты анализа**: `[сущность]_[тип]_[дата].md` или `.json`

## Управление архивом

### Директория архива (`archive/`)
Содержит устаревший код, организованный по:
- `old_scripts/` - Устаревшие утилитарные скрипты
- `old_tests/` - Исторические тестовые файлы
- `old_docs/` - Устаревшая документация
- `experiments/` - Код proof-of-concept

### Руководящие принципы миграции
- Перемещать устаревший код в `archive/` с четким именованием
- Поддерживать `README.md` в архиве, объясняющий что было перемещено и почему
- Держать архив организованным по дате и функциональности

## Независимость проектов

### Oracul Bot
- **Фокус**: Самоанализ диалогов пользователей
- **Зависимости**: Минимальные (Telethon, OpenRouter)
- **Развертывание**: Простой Python скрипт
- **Цель**: Личное использование и самопознание

### Analysis Engine
- **Фокус**: Анализ каналов, карьерные исследования
- **Зависимости**: Минимальные (Telethon, OpenRouter, CLIProxyAPI)
- **Развертывание**: Простые Python скрипты
- **Цель**: Бизнес-аналитика и исследования
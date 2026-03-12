# 🚀 TG Analysis Platform - Инструкции по установке

## Быстрая установка

### 1. Скопируйте всю папку `tg-analysis-platform` в ваш новый репозиторий:
```bash
cp -r tg-analysis-platform/* C:/Users/temsan/IdeaProjects/tg-analysis-platform/
```

### 2. Перейдите в директорию проекта:
```bash
cd C:/Users/temsan/IdeaProjects/tg-analysis-platform
```

### 3. Настройте окружение:
```bash
# Backend
cd backend
cp .env.example .env
# Отредактируйте .env файл с вашими настройками

# Установите зависимости
pip install -r requirements.txt
```

### 4. Получите Telegram API ключи:
1. Перейдите на https://my.telegram.org/apps
2. Создайте новое приложение
3. Скопируйте API ID и API Hash в `.env` файл

### 5. Запустите проект:
```bash
# С Docker (рекомендуется)
docker-compose up -d

# Или без Docker
cd backend
uvicorn app.main:app --reload
```

### 6. Откройте в браузере:
- API документация: http://localhost:8000/docs
- Главная страница: http://localhost:8000

## Что уже готово:

### ✅ Backend (FastAPI)
- Полная структура API
- Авторизация через Telegram
- Сбор данных из Telegram
- 3 анализатора (Big Five, Hero's Journey, Destiny Axis)
- Генерация PDF отчетов
- База данных (PostgreSQL)
- Кэширование (Redis)
- Фоновые задачи (Celery)

### ✅ Анализаторы
- **Big Five Personality** - научный анализ личности
- **Hero's Journey** - путь героя по Кэмпбеллу
- **Destiny Axis** - ось судьбы по методу Краша

### ✅ Инфраструктура
- Docker контейнеры
- База данных
- Логирование
- Конфигурация

## Следующие шаги:

### 1. Frontend (React) - 2 недели
- Создать React приложение
- Компоненты для загрузки данных
- Отображение результатов анализа
- Скачивание отчетов

### 2. Дополнительные анализаторы - 2 недели
- Shadow Work Analyzer
- Archetypes Analyzer
- Astrological Analyzer
- Numerology Analyzer

### 3. Улучшения - 2 недели
- Реальная генерация PDF
- Интерактивные визуализации
- Система подписок
- Мобильная версия

## Структура проекта:

```
tg-analysis-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── analyzers/      # Анализаторы личности
│   │   ├── collectors/     # Сборщики данных Telegram
│   │   ├── generators/     # Генераторы отчетов
│   │   ├── models/         # Модели базы данных
│   │   └── core/           # Основные модули
│   ├── requirements.txt    # Python зависимости
│   └── Dockerfile         # Docker образ
├── frontend/              # React frontend (создать)
├── docs/                  # Документация
└── docker-compose.yml     # Docker конфигурация
```

## Готово к разработке! 🎉

Вся архитектура создана, основные компоненты реализованы. 
Можно сразу начинать тестировать API и добавлять новые функции.

**Ваша "Ось Судьбы" в действии - от концепции к реализации за один день!** 🌟
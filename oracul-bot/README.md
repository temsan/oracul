# 🔮 Oracul Bot - AI-бот для самоанализа диалогов

Персональный AI-бот для глубокого анализа собственных Telegram диалогов и психологического самопознания. Система обеспечивает этичное профилирование личности через мультимодальный анализ текста, голоса и изображений.

## 🚀 Быстрый запуск

### 1. Получите BOT_TOKEN
1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Создайте нового бота: `/newbot`
3. Скопируйте полученный токен

### 2. Настройте конфигурацию
```bash
# Отредактируйте файл .env
BOT_TOKEN=ваш_токен_бота
```

### 3. Запустите бота
```bash
# Единая точка запуска (из корня проекта)
cd ..
python run.py                 # Только бот
python run.py --webapp        # Бот + Web App
python run.py --webapp-only   # Только Web App

# Или напрямую:
cd oracul-bot
python unified_bot.py
```

### 4. Web App для управления сессиями (опционально)
```bash
# Через единый лаунчер
python run.py --webapp-only

# Или напрямую:
pip install fastapi uvicorn
uvicorn session_webapp:app --host 0.0.0.0 --port 8088
```

## 📋 Статус проекта

✅ **Структура:** Готова  
✅ **Зависимости:** Установлены  
✅ **Unified Bot:** Работает с системой сессий  
✅ **Сессии:** Поддержка TTL и временных сессий  
✅ **Web App:** Готов к использованию  
⚠️ **Конфигурация:** Требует BOT_TOKEN  

## 🔧 Доступные версии

### 🔹 Simple Bot (Рекомендуется)
```bash
python simple_bot.py
```
- Минимальные зависимости
- Базовый анализ чатов
- Простая статистика и тональность

### 🔹 Unified Bot (Полная версия)
```bash
python unified_bot.py
```
- Полный функционал
- AI анализ через OpenRouter
- Психологические анализы

### 🔹 Original Bot
```bash
python bot_self_analysis.py
```
- Оригинальная версия
- Фокус на самоанализе

## 🔐 Система сессий

Каждый пользователь авторизуется через свой Telegram-аккаунт:

- **Режим TTL (постоянный)** — сессия с ограниченным временем жизни, автоматически продлевается
- **Режим Временный** — одноразовая сессия, удаляется после запроса
- **Настраиваемое TTL** — от 15 минут до 1 дня

### Команды
```
/login  — Войти в личную сессию
/logout — Выйти из сессии
```

### Настройка в .env
```env
DEFAULT_SESSION_TTL_MINUTES=60
SESSION_TTL_OPTIONS_MINUTES=15,60,180,720,1440
DEFAULT_SESSION_MODE=persistent
SESSION_WEB_APP_URL=https://your-domain.com:8088
```

## 💰 Монетизация

- **Free:** 30 анализов/месяц
- **Premium:** 199₽/мес - полный анализ
- **Pro:** 499₽/мес - консультации

## 🔧 Конфигурация

### Основные переменные окружения

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com

# OpenAI
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/oracul_db
REDIS_URL=redis://localhost:6379/0

# Business Logic
FREE_ANALYSES_PER_MONTH=30
PREMIUM_PRICE_RUB=199
PRO_PRICE_RUB=499
```

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С покрытием кода
pytest --cov=. --cov-report=html
```

## 🚀 Развертывание

### Docker Deployment

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f oracul-bot
```

## 📈 Roadmap

### Q1 2025 - MVP
- [x] Базовая архитектура
- [x] Анализ текста
- [x] Анализ голоса
- [x] Telegram Bot интерфейс
- [ ] Система подписок
- [ ] Beta тестирование

### Q2 2025 - Enhanced Features
- [ ] Анализ видео
- [ ] Расширенные инсайты
- [ ] Web интерфейс
- [ ] API для партнеров

---

**🔮 Oracul - от анализа к инсайтам, от инсайтов к росту!**
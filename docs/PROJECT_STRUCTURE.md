# 🗂️ Структура проекта TG Analysis Platform

**Обновлено:** 24 декабря 2025  
**Статус:** Реорганизовано по функциональным задачам

---

## 📁 Корневая структура

```
tg-analysis-platform/
├── 📂 scripts/                    # Исполняемые скрипты
│   ├── 🔄 telegram_data_collection/  # Сбор данных из Telegram
│   ├── 👤 user_analysis/             # Анализ пользователей
│   ├── 📺 channel_analysis/          # Анализ каналов
│   ├── 💼 career_job_search/         # Карьера и поиск работы
│   ├── ⚙️ system_setup/             # Настройка системы
│   └── 📋 README.md                 # Документация скриптов
├── 📂 analysis/                   # Результаты анализа
│   ├── 👤 user_profiles/            # Профили пользователей
│   ├── 📺 channel_research/         # Исследования каналов
│   ├── 💼 career_development/       # Карьерное развитие
│   ├── 🗃️ raw_data/                # Сырые данные
│   └── 📋 README.md                # Документация анализов
├── 📂 backend/                    # Backend API
├── 📂 telegram-bot/               # Telegram бот
├── 🔧 .env                        # Конфигурация
├── 🐳 docker-compose.yml          # Docker setup
└── 📖 README.md                   # Основная документация
```

---

## 🎯 Функциональные области

### 🔄 Сбор данных (`scripts/telegram_data_collection/`)
**Задачи:** Извлечение информации из Telegram API
- `collect_and_analyze.py` - Основной сборщик пользовательских данных
- `get_bot_chat.py` - Переписки с ботами
- `get_channel_*.py` - Контент каналов
- `get_message_*.py` - Конкретные сообщения

### 👤 Анализ пользователей (`scripts/user_analysis/`)
**Задачи:** Психологическое профилирование и поведенческий анализ
- `analyze_participants.py` - Анализ участников чатов
- `analyze_specific_user.py` - Глубокий анализ пользователя
- `multimodal_analyzer.py` - Мультимодальный анализ (текст + голос + фото)

### 📺 Анализ каналов (`scripts/channel_analysis/`)
**Задачи:** Исследование контента и влияния каналов
- `analyze_through_channels.py` - Анализ через призму каналов
- `channel_summary.py` - Саммари каналов
- `pickup_summary.py` - Специализированный анализ пикап-контента

### 💼 Карьера (`scripts/career_job_search/`)
**Задачи:** Поиск работы и карьерное развитие
- `get_job_market_post.py` - Мониторинг рынка труда

### ⚙️ Система (`scripts/system_setup/`)
**Задачи:** Настройка окружения и тестирование
- `setup_env.py` - Инициализация проекта
- `test_*.py` - Тестовые скрипты
- `update_models.py` - Обновление AI моделей

---

## 📊 Результаты анализа

### 👤 Профили пользователей (`analysis/user_profiles/`)
**Содержит:** Психологические анализы и поведенческие паттерны
- Big Five личностные профили
- Jungian архетипы и типология
- Attachment styles и отношения
- Токсичные связи и рекомендации

### 📺 Исследования каналов (`analysis/channel_research/`)
**Содержит:** Анализ контента и влияния Telegram каналов
- Тематические саммари каналов
- Сравнительные исследования
- Влияние на поведение пользователей
- Рекомендации по потреблению контента

### 💼 Карьерное развитие (`analysis/career_development/`)
**Содержит:** Материалы для поиска работы и развития карьеры
- ✅ **`resume_optimized_2025.md`** - Финальное резюме
- ✅ **`job_search_strategy_2025.md`** - Стратегия поиска работы
- ✅ **`t_shape_legend_analysis.md`** - T-shaped позиционирование
- 📊 Анализ рынка труда и рекомендации ОМ

### 🗃️ Сырые данные (`analysis/raw_data/`)
**Содержит:** Исходные данные для анализа
- JSON файлы с сообщениями и метаданными
- TXT дампы каналов и чатов
- Мультимодальные данные (голос, фото)

---

## 🚀 Быстрый старт

### Сбор данных:
```bash
# Анализ пользователя
python scripts/user_analysis/multimodal_analyzer.py

# Анализ каналов
python scripts/channel_analysis/channel_summary.py

# Сбор данных из Telegram
python scripts/telegram_data_collection/collect_and_analyze.py
```

### Карьерные материалы:
```bash
# Актуальное резюме
cat analysis/career_development/resume_optimized_2025.md

# Стратегия поиска работы
cat analysis/career_development/job_search_strategy_2025.md

# T-shaped позиционирование
cat analysis/career_development/t_shape_legend_analysis.md
```

### Настройка системы:
```bash
# Первоначальная настройка
python scripts/system_setup/setup_env.py

# Тестирование
python scripts/system_setup/test_env_priority.py
```

---

## 🎯 Актуальные задачи (декабрь 2025)

### ✅ Завершенные:
- [x] Создание AI-платформы анализа Telegram
- [x] Мультимодальный анализ пользователей
- [x] Исследование каналов и их влияния
- [x] Оптимизация резюме под рынок 2025
- [x] T-shaped позиционирование для карьеры
- [x] Реорганизация структуры проекта

### 🔄 В процессе:
- [ ] Поиск работы AI Solutions Architect
- [ ] Подача резюме в целевые компании
- [ ] Подготовка к техническим собеседованиям

### 📋 Планируемые:
- [ ] Создание GitHub портфолио
- [ ] Развитие личного бренда в AI
- [ ] Менторство и обучение

---

## 🔧 Технический стек

### Backend & AI:
- **Python:** FastAPI, asyncio, aiogram
- **AI/ML:** LangChain, PyTorch, Transformers, RAG
- **Databases:** PostgreSQL, Redis, Vector DBs
- **Infrastructure:** Docker, Kubernetes, AWS

### Data Collection:
- **Telegram API:** telethon для сбора данных
- **OpenRouter API:** AI анализ через LLM
- **Multimodal:** обработка текста, голоса, изображений

### Configuration:
- **Environment:** python-dotenv для настроек
- **Models:** openai/gpt-oss-120b:free (основная)
- **Backup:** openai/gpt-oss-20b:free (резервная)

---

## 📈 Архетип проекта

**Алхимик (0,9%)** - трансформация данных в инсайты:
- **Исследователь:** Глубокое изучение поведенческих паттернов
- **Деятель:** Практическая реализация AI-решений
- **Концептуальный:** Системное видение и архитектурный подход

**Результат:** Уникальная платформа для анализа и карьерного развития через AI
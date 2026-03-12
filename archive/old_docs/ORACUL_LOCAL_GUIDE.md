# 🔮 ORACUL BOT - Локальные модели

## Полностью автономная версия с локальными AI-моделями

**Преимущества локальной версии:**
- 🔒 **Полная приватность** - данные не покидают ваш сервер
- ⚡ **Высокая скорость** - нет задержек API запросов
- 🌐 **Автономность** - работа без интернета
- 💰 **Экономия** - нет платы за API вызовы
- 🎛️ **Полный контроль** - настройка моделей под ваши нужды

---

## 🛠️ Системные требования

### Минимальные требования:
- **CPU**: 4+ ядра
- **RAM**: 8GB (рекомендуется 16GB+)
- **Диск**: 20GB свободного места
- **Python**: 3.11+

### Рекомендуемые требования:
- **GPU**: NVIDIA с 8GB+ VRAM (для ускорения)
- **RAM**: 32GB+ (для больших моделей)
- **Диск**: SSD 50GB+

---

## 📦 Установка

### 1. Клонирование и зависимости

```bash
cd oracul-bot

# Создаем виртуальное окружение
python -m venv venv_local
source venv_local/bin/activate  # Linux/Mac
# или
venv_local\Scripts\activate     # Windows

# Устанавливаем зависимости для локальных моделей
pip install -r requirements_local.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env файл
```

### 3. Настройка для GPU (опционально)

```bash
# Для NVIDIA GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Проверка CUDA
python -c "import torch; print(f'CUDA доступна: {torch.cuda.is_available()}')"
```

---

## 🧠 Локальные модели

### Текстовый анализ:
- **RuBERT** (`blanchefort/rubert-base-cased-sentiment`) - тональность на русском
- **DistilRoBERTa** (`j-hartmann/emotion-english-distilroberta-base`) - эмоции
- **DeepPavlov** (`DeepPavlov/rubert-base-cased-sentence`) - эмбеддинги
- **RuGPT** (`ai-forever/rugpt3small_based_on_gpt2`) - генерация текста

### Голосовой анализ:
- **Whisper** (`whisper-base`) - транскрипция речи
- **librosa** - анализ аудио характеристик

### Высокопроизводительный inference:
- **vLLM** - оптимизированный inference для LLM

---

## ⚡ Настройка vLLM (рекомендуется)

vLLM обеспечивает высокопроизводительный inference локальных LLM:

### Установка:
```bash
pip install vllm
```

### Запуск сервера:
```bash
# Базовая модель
python -m vllm.entrypoints.api_server \
    --model microsoft/DialoGPT-medium \
    --host 0.0.0.0 \
    --port 8000

# Русская модель
python -m vllm.entrypoints.api_server \
    --model ai-forever/rugpt3small_based_on_gpt2 \
    --host 0.0.0.0 \
    --port 8000

# С GPU оптимизацией
python -m vllm.entrypoints.api_server \
    --model microsoft/DialoGPT-medium \
    --tensor-parallel-size 1 \
    --dtype float16
```

---

## 🚀 Запуск

### Вариант 1: Простой запуск
```bash
python run_local.py
```

### Вариант 2: Ручной запуск
```bash
python main_local.py
```

### Вариант 3: Docker (рекомендуется для продакшена)

```bash
# С GPU поддержкой
docker-compose -f docker-compose-local.yml --profile gpu up -d

# Только CPU
docker-compose -f docker-compose-local.yml --profile cpu up -d
```

---

## 🔧 Конфигурация

### Основные настройки в .env:

```env
# Обязательные
TELEGRAM_BOT_TOKEN=your-bot-token
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/oracul_db

# Локальные модели
FORCE_CPU=false  # true для принудительного использования CPU
VLLM_API_URL=http://localhost:8000  # URL vLLM сервера

# Кеширование моделей
MODEL_CACHE_DIR=/app/models
WHISPER_CACHE_DIR=/root/.cache/whisper
```

---

## 📊 Мониторинг

### Проверка статуса:
```bash
# Статус всех компонентов
curl http://localhost:8001/health

# Статус моделей
curl http://localhost:8001/models

# Статус vLLM
curl http://localhost:8000/health
```

### Команды бота:
- `/start` - главное меню с локальными возможностями
- `/models` - информация о загруженных моделях
- `/vllm` - статус vLLM сервера
- `/help` - справка по локальным функциям

---

## 🎯 Функции локальной версии

### 🧠 Локальный анализ текста:
- Анализ тональности с RuBERT
- Определение эмоций с DistilRoBERTa
- Личностные тенденции через эмбеддинги
- Генеративный анализ с vLLM

### 🎤 Whisper анализ голоса:
- Транскрипция с Whisper
- Аудио характеристики с librosa
- Эмоциональные маркеры в речи
- Параметры голоса и интонации

### 📺 Анализ каналов:
- Работает через Telethon (как в обычной версии)
- Дополнительный анализ контента локальными моделями

---

## 🔍 Устранение неполадок

### Проблема: "CUDA out of memory"
**Решение:**
```bash
# Уменьшите размер модели
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Или используйте CPU
export FORCE_CPU=true
```

### Проблема: "Model not found"
**Решение:**
```bash
# Предварительная загрузка моделей
python -c "
import whisper
from transformers import AutoTokenizer, AutoModel
whisper.load_model('base')
AutoTokenizer.from_pretrained('blanchefort/rubert-base-cased-sentiment')
"
```

### Проблема: "vLLM server unavailable"
**Решение:**
```bash
# Запустите vLLM сервер отдельно
python -m vllm.entrypoints.api_server --model microsoft/DialoGPT-medium

# Или отключите vLLM в настройках
export VLLM_ENABLED=false
```

### Проблема: Медленная работа
**Решение:**
- Используйте GPU если доступно
- Уменьшите размер моделей
- Включите кеширование моделей
- Используйте vLLM для LLM inference

---

## 📈 Производительность

### Время анализа (примерно):

**С GPU:**
- Текст: 0.5-2 секунды
- Голос (30 сек): 3-8 секунд
- vLLM генерация: 1-3 секунды

**Только CPU:**
- Текст: 2-10 секунд
- Голос (30 сек): 10-30 секунд
- Генерация: 10-60 секунд

### Использование памяти:
- Базовые модели: ~2-4GB RAM
- Все модели: ~8-12GB RAM
- С vLLM: +2-8GB в зависимости от модели

---

## 🔒 Приватность и безопасность

### Гарантии приватности:
- ✅ Все данные обрабатываются локально
- ✅ Нет отправки данных в интернет
- ✅ Полный контроль над моделями
- ✅ Возможность работы offline

### Рекомендации:
- Используйте файрвол для блокировки исходящих соединений
- Регулярно обновляйте модели
- Настройте логирование для аудита
- Используйте шифрование диска

---

## 🚀 Развертывание в продакшене

### Docker Compose:
```bash
# Полная конфигурация с GPU
docker-compose -f docker-compose-local.yml --profile gpu --profile production up -d
```

### Kubernetes:
```yaml
# Пример конфигурации для K8s
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oracul-local
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: oracul-bot
        image: oracul-bot:local
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: "8Gi"
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
```

---

## 📞 Поддержка

### Если возникли проблемы:
1. Проверьте системные требования
2. Убедитесь в корректности .env файла
3. Проверьте логи: `docker-compose logs -f oracul-bot-local`
4. Обратитесь в поддержку: @oracul_support

### Полезные ссылки:
- [Документация vLLM](https://vllm.readthedocs.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [OpenAI Whisper](https://github.com/openai/whisper)

---

**🔮 Oracul Local - максимальная приватность и производительность!**

*Ваши данные остаются у вас. Ваши модели работают для вас.*
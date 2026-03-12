# 🎮 Настройка RTX 2050 для локальных LLM

## 🎯 **Оптимизация для RTX 2050 (4GB VRAM)**

### 📊 **Характеристики RTX 2050:**
- **VRAM**: 4GB GDDR6
- **CUDA Cores**: 2048
- **Memory Bandwidth**: 112 GB/s
- **Compute Capability**: 8.6

---

## 🚀 **Быстрая настройка**

### 1️⃣ **Установка CUDA PyTorch**
```bash
# Для RTX 2050 используйте CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Или CUDA 12.1 (новее)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2️⃣ **Установка зависимостей**
```bash
cd backend/
pip install -r requirements.txt

# Дополнительно для оптимизации
pip install bitsandbytes accelerate
```

### 3️⃣ **Настройка .env файла**
```env
# Локальные LLM настройки для RTX 2050
LLM_STRATEGY=auto
USE_CUDA=true
CUDA_DEVICE=auto
USE_8BIT_QUANTIZATION=true
USE_4BIT_QUANTIZATION=false
MAX_MEMORY_GB=3.5
LOCAL_MODEL_NAME=microsoft/DialoGPT-medium
PREFER_LOCAL_MODELS=true
```

---

## 🔧 **Оптимальные настройки**

### ⚡ **Для максимальной скорости:**
```env
LOCAL_MODEL_NAME=microsoft/DialoGPT-small
USE_8BIT_QUANTIZATION=true
MAX_MEMORY_GB=2.0
```

### 🎯 **Для баланса качества и скорости:**
```env
LOCAL_MODEL_NAME=microsoft/DialoGPT-medium
USE_8BIT_QUANTIZATION=true
MAX_MEMORY_GB=3.5
```

### 💾 **Для экономии памяти (если мало VRAM):**
```env
LOCAL_MODEL_NAME=distilgpt2
USE_4BIT_QUANTIZATION=true
MAX_MEMORY_GB=2.0
```

---

## 📊 **Рекомендуемые модели**

### 🟢 **Оптимальные для RTX 2050:**

| Модель | Размер | VRAM | Скорость | Качество |
|--------|--------|------|----------|----------|
| DialoGPT-small | ~117MB | ~1GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| DialoGPT-medium | ~345MB | ~2GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| DistilGPT2 | ~319MB | ~1.5GB | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### 🟡 **Возможные с квантизацией:**

| Модель | Размер | VRAM (8bit) | Скорость | Качество |
|--------|--------|-------------|----------|----------|
| GPT2 | ~548MB | ~2.5GB | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| GPT2-medium | ~1.4GB | ~3.5GB | ⭐⭐ | ⭐⭐⭐⭐⭐ |

### 🔴 **Не рекомендуется:**
- GPT2-large (слишком большая для 4GB)
- LLaMA модели (требуют больше памяти)
- Модели больше 1GB без квантизации

---

## 🧪 **Тестирование производительности**

### 📈 **Запуск тестов:**
```bash
cd backend/
python test_rtx2050.py
```

### 📊 **Ожидаемые результаты:**
```
🎮 ТЕСТ НАСТРОЙКИ RTX 2050
CUDA доступна: True
GPU 0: NVIDIA GeForce RTX 2050
  Память: 4.0GB
  Свободно: 3.5GB

🤖 ТЕСТ ЗАГРУЗКИ МОДЕЛЕЙ
DialoGPT-small: ✅ Загружена за 2.3с (1.1GB)
DialoGPT-medium: ✅ Загружена за 4.1с (2.2GB)

⚡ ТЕСТ СКОРОСТИ ИНФЕРЕНСА
Короткий текст: 0.8с
Средний текст: 1.2с
Длинный текст: 2.1с
```

---

## 🎯 **Стратегии использования**

### 🔄 **Гибридный подход (рекомендуется):**
```python
# Автоматический выбор модели
LLM_STRATEGY=auto

# Локальные модели для:
- Big Five анализ
- Психологические типы
- Короткие тексты (< 1000 символов)

# OpenRouter для:
- Архетипы Юнга
- Теневая работа
- Сложные анализы
- Длинные тексты (> 1000 символов)
```

### ⚡ **Только локальные модели:**
```python
LLM_STRATEGY=local
PREFER_LOCAL_MODELS=true

# Плюсы:
+ Бесплатно
+ Приватность
+ Быстрый отклик

# Минусы:
- Ниже качество для сложных задач
- Ограниченный контекст
```

### ☁️ **Только OpenRouter:**
```python
LLM_STRATEGY=openrouter

# Плюсы:
+ Высокое качество
+ Большой контекст
+ Продвинутые модели

# Минусы:
- Стоимость API
- Зависимость от интернета
```

---

## 🔧 **Устранение проблем**

### ❌ **"CUDA out of memory"**
```env
# Уменьшите модель
LOCAL_MODEL_NAME=microsoft/DialoGPT-small

# Включите 4bit квантизацию
USE_4BIT_QUANTIZATION=true

# Уменьшите лимит памяти
MAX_MEMORY_GB=2.0
```

### ❌ **"Model loading failed"**
```bash
# Очистите кэш
rm -rf models_cache/

# Проверьте CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Переустановите PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### ❌ **Медленная работа**
```env
# Проверьте что используется GPU
USE_CUDA=true
CUDA_DEVICE=cuda:0

# Используйте меньшую модель
LOCAL_MODEL_NAME=microsoft/DialoGPT-small

# Включите квантизацию
USE_8BIT_QUANTIZATION=true
```

---

## 📊 **Мониторинг производительности**

### 🎮 **Команды в Telegram Bot:**
```
/models - статус моделей и памяти GPU
/stats - общая статистика производительности
```

### 💻 **Мониторинг GPU:**
```bash
# Использование GPU
nvidia-smi

# Мониторинг в реальном времени
watch -n 1 nvidia-smi

# Температура и частоты
nvidia-smi -q -d TEMPERATURE,CLOCK
```

### 📈 **Логи производительности:**
```bash
# Логи локального LLM
tail -f backend/logs/local_llm.log

# Метрики анализов
python backend/monitor_quality.py
```

---

## 🎯 **Рекомендации по использованию**

### ✅ **Лучшие практики:**
1. **Используйте гибридный режим** для оптимального баланса
2. **Мониторьте память GPU** через `/models` команду
3. **Настройте квантизацию** под ваши задачи
4. **Тестируйте разные модели** для ваших данных
5. **Очищайте память** между сессиями если нужно

### 🎮 **Оптимизация для RTX 2050:**
- **8bit квантизация** - оптимальный выбор
- **DialoGPT-medium** - лучший баланс качества/скорости
- **Автоматический выбор** модели по типу задачи
- **Fallback на OpenRouter** для сложных случаев

### 💡 **Экономия ресурсов:**
- Используйте локальные модели для простых анализов
- OpenRouter только для продвинутых анализаторов
- Мониторьте затраты через метрики
- A/B тестируйте качество разных подходов

---

**Готово! Теперь у вас есть оптимизированная настройка для RTX 2050 с гибридным использованием локальных и облачных моделей.** 🚀
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Системные зависимости (ffmpeg для аудио)
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Зависимости (из корня проекта, контекст сборки — корень)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код бота
COPY oracul-bot/ ./oracul-bot/
COPY .env ./

WORKDIR /app/oracul-bot

# Non-root user
RUN useradd --create-home --shell /bin/bash oracul \
    && chown -R oracul:oracul /app
USER oracul

CMD ["python", "unified_bot.py"]

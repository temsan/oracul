#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест расшифровки голоса через Groq Whisper API
"""

import asyncio
import sys
import logging
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from analyzers.voice_analyzer import VoiceAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_groq_connection():
    """Проверка подключения к Groq API"""
    print("[*] Проверка подключения к Groq API...")

    try:
        import openai

        # Создаем клиент
        client = openai.AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL
        )

        # Проверяем, что ключ загружен
        if not settings.GROQ_API_KEY:
            print("[X] GROQ_API_KEY не найден в .env")
            return False

        print(f"[OK] Groq API URL: {settings.GROQ_BASE_URL}")
        print(f"[OK] Модель Whisper: {settings.GROQ_WHISPER_MODEL}")
        print(f"[OK] API ключ загружен: {settings.GROQ_API_KEY[:10]}...")

        return True

    except Exception as e:
        print(f"[X] Ошибка подключения к Groq API: {e}")
        return False


async def test_voice_analyzer_init():
    """Проверка инициализации VoiceAnalyzer"""
    print("\n[*] Проверка инициализации VoiceAnalyzer...")

    try:
        analyzer = VoiceAnalyzer()

        print("[OK] VoiceAnalyzer успешно создан")
        print(f"[OK] Клиент настроен на: {settings.GROQ_BASE_URL}")

        return True

    except Exception as e:
        print(f"[X] Ошибка инициализации VoiceAnalyzer: {e}")
        return False


async def test_settings():
    """Проверка настроек"""
    print("\n[*] Проверка настроек...")

    try:
        if not settings:
            print("[X] Настройки не загружены")
            return False

        print(f"[OK] DEBUG: {settings.DEBUG}")
        print(f"[OK] GROQ_API_KEY: {'установлен' if settings.GROQ_API_KEY else 'НЕ установлен'}")
        print(f"[OK] GROQ_BASE_URL: {settings.GROQ_BASE_URL}")
        print(f"[OK] GROQ_WHISPER_MODEL: {settings.GROQ_WHISPER_MODEL}")

        return True

    except Exception as e:
        print(f"[X] Ошибка проверки настроек: {e}")
        return False


async def main():
    """Главная функция тестирования"""
    print("Тестирование Groq Voice Transcription")
    print("=" * 50)

    # Запускаем тесты
    results = []

    # Тест настроек
    settings_result = await test_settings()
    results.append(("Settings", settings_result))

    # Тест подключения к Groq
    groq_result = await test_groq_connection()
    results.append(("Groq Connection", groq_result))

    # Тест инициализации анализатора
    analyzer_result = await test_voice_analyzer_init()
    results.append(("VoiceAnalyzer Init", analyzer_result))

    # Итоги
    print("\n" + "=" * 50)
    print("Результаты тестирования:")

    for test_name, result in results:
        status = "[OK] Пройден" if result else "[X] Не пройден"
        print(f"  {test_name}: {status}")

    success_count = sum(1 for _, result in results if result)
    total_count = len(results)

    print(f"\nИтого: {success_count}/{total_count} тестов пройдено")

    if success_count == total_count:
        print("[OK] Все тесты пройдены! Groq Voice Analyzer готов к работе.")
        print("\n[!] Для полной проверки отправьте голосовое сообщение боту в Telegram.")
    elif success_count > 0:
        print("[!] Анализатор частично готов. Проверьте настройки в .env")
    else:
        print("[X] Анализатор не готов. Проверьте GROQ_API_KEY в .env")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Тест локального анализатора голоса
"""

import asyncio
import sys
import logging
import tempfile
import numpy as np
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.local_voice_analyzer import LocalVoiceAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_audio():
    """Создание тестового аудио файла"""
    try:
        import soundfile as sf
        
        # Создаем простой синусоидальный сигнал
        duration = 3  # секунды
        sample_rate = 16000
        frequency = 440  # Hz (нота A)
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Добавляем небольшой шум для реалистичности
        noise = 0.01 * np.random.randn(len(audio_data))
        audio_data += noise
        
        # Сохраняем во временный файл
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_file.name, audio_data, sample_rate)
        
        return temp_file.name, duration
        
    except Exception as e:
        logger.error(f"Ошибка создания тестового аудио: {e}")
        return None, 0


class MockVoiceFile:
    """Мок объект для имитации голосового файла Telegram"""
    
    def __init__(self, file_path):
        self.file_path = file_path
    
    async def download_to_drive(self, destination):
        """Имитация скачивания файла"""
        import shutil
        shutil.copy2(self.file_path, destination)


async def test_voice_analyzer():
    """Тест локального анализатора голоса"""
    print("🎤 Тестирование локального анализатора голоса...")
    
    try:
        # Создаем тестовый аудио файл
        audio_path, duration = create_test_audio()
        
        if not audio_path:
            print("❌ Не удалось создать тестовый аудио файл")
            return False
        
        print(f"📁 Создан тестовый аудио файл: {duration} сек")
        
        # Инициализируем анализатор
        analyzer = LocalVoiceAnalyzer()
        
        # Создаем мок файла
        mock_file = MockVoiceFile(audio_path)
        
        # Анализируем
        result = await analyzer.analyze(mock_file, duration)
        
        if result.get('success'):
            print("✅ Анализ голоса успешен")
            
            # Аудио характеристики
            audio_features = result.get('audio_features', {})
            if audio_features:
                interpretation = audio_features.get('interpretation', {})
                print(f"🔊 Аудио характеристики:")
                for key, value in interpretation.items():
                    print(f"  • {key}: {value}")
            
            # Транскрипция (будет пустой для синтетического аудио)
            transcription_analysis = result.get('transcription_analysis', {})
            transcription = transcription_analysis.get('transcription', '')
            if transcription:
                print(f"📝 Транскрипция: {transcription}")
            else:
                print("📝 Транскрипция: (синтетический сигнал без речи)")
            
            # Рекомендации
            recommendations = result.get('recommendations', [])
            if recommendations:
                print(f"💡 Наблюдения: {'; '.join(recommendations)}")
            
        else:
            print(f"❌ Ошибка анализа: {result.get('error', 'Unknown error')}")
            return False
        
        # Удаляем временный файл
        import os
        os.unlink(audio_path)
        
        print("✅ Тест анализатора голоса завершен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования анализатора голоса: {e}")
        return False


async def test_whisper_loading():
    """Тест загрузки Whisper"""
    print("\n🎤 Тестирование загрузки Whisper...")
    
    try:
        import whisper
        
        print("📥 Загрузка Whisper base модели...")
        model = whisper.load_model("base")
        print("✅ Whisper base успешно загружен")
        
        # Тест транскрипции с пустым аудио
        print("🔍 Тест базовой функциональности...")
        
        # Создаем минимальный аудио массив
        import numpy as np
        dummy_audio = np.zeros(16000)  # 1 секунда тишины
        
        result = model.transcribe(dummy_audio, language="ru")
        print(f"📝 Тест транскрипции: '{result['text']}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Whisper: {e}")
        return False


async def test_librosa_features():
    """Тест извлечения аудио признаков с librosa"""
    print("\n🔊 Тестирование librosa...")
    
    try:
        import librosa
        import numpy as np
        
        # Создаем тестовый сигнал
        duration = 2
        sr = 22050
        t = np.linspace(0, duration, int(sr * duration))
        y = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz синус
        
        print("📊 Извлечение аудио признаков...")
        
        # Основные признаки
        rms = librosa.feature.rms(y=y)[0]
        print(f"  • RMS энергия: {np.mean(rms):.4f}")
        
        # MFCC
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        print(f"  • MFCC коэффициенты: {mfccs.shape}")
        
        # Спектральный центроид
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        print(f"  • Спектральный центроид: {np.mean(spectral_centroids):.2f} Hz")
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        print(f"  • Zero crossing rate: {np.mean(zcr):.4f}")
        
        print("✅ librosa функции работают корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования librosa: {e}")
        return False


async def main():
    """Главная функция тестирования голосового анализатора"""
    print("🎤 Тестирование Oracul Voice Analyzer")
    print("=" * 50)
    
    # Проверяем зависимости
    try:
        import whisper
        print("✅ Whisper доступен")
    except ImportError:
        print("❌ Whisper не установлен")
    
    try:
        import librosa
        print("✅ librosa доступен")
    except ImportError:
        print("❌ librosa не установлен")
    
    try:
        import soundfile
        print("✅ soundfile доступен")
    except ImportError:
        print("❌ soundfile не установлен")
    
    print("\n" + "=" * 50)
    
    # Запускаем тесты
    results = []
    
    # Тест Whisper
    whisper_result = await test_whisper_loading()
    results.append(("Whisper Loading", whisper_result))
    
    # Тест librosa
    librosa_result = await test_librosa_features()
    results.append(("Librosa Features", librosa_result))
    
    # Тест полного анализатора
    analyzer_result = await test_voice_analyzer()
    results.append(("Voice Analyzer", analyzer_result))
    
    # Итоги
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:")
    
    for test_name, result in results:
        status = "✅ Пройден" if result else "❌ Не пройден"
        print(f"  {test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n🎯 Итого: {success_count}/{total_count} тестов пройдено")
    
    if success_count == total_count:
        print("🎉 Все тесты пройдены! Голосовой анализатор готов к работе.")
    elif success_count > 0:
        print("⚠️ Анализатор частично готов. Некоторые функции могут быть ограничены.")
    else:
        print("❌ Анализатор не готов. Проверьте установку зависимостей.")


if __name__ == "__main__":
    asyncio.run(main())
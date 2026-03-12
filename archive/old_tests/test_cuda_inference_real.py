#!/usr/bin/env python3
"""
Реальный CUDA inference с мониторингом памяти
"""

import asyncio
import sys
import time
import gc
from pathlib import Path
import logging
import psutil
import os

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / 'oracul-bot'))

import torch
from analyzers.local_text_analyzer import LocalTextAnalyzer
from analyzers.local_voice_analyzer import LocalVoiceAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CUDAInferenceMonitor:
    """Мониторинг CUDA inference с точными метриками"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.text_analyzer = None
        self.voice_analyzer = None
        
    def get_memory_info(self):
        """Получить информацию о памяти"""
        # RAM
        memory_info = self.process.memory_info()
        ram_mb = memory_info.rss / 1024 / 1024
        
        # GPU память
        gpu_info = {}
        if torch.cuda.is_available():
            gpu_info = {
                'allocated': torch.cuda.memory_allocated() / 1024 / 1024,
                'cached': torch.cuda.memory_reserved() / 1024 / 1024,
                'max_allocated': torch.cuda.max_memory_allocated() / 1024 / 1024
            }
        
        return {
            'ram_mb': ram_mb,
            'gpu': gpu_info
        }
    
    def print_memory_status(self, stage: str):
        """Вывести статус памяти"""
        mem_info = self.get_memory_info()
        print(f"\n💾 {stage}:")
        print(f"  RAM: {mem_info['ram_mb']:.1f} MB")
        
        if mem_info['gpu']:
            print(f"  GPU Allocated: {mem_info['gpu']['allocated']:.1f} MB")
            print(f"  GPU Cached: {mem_info['gpu']['cached']:.1f} MB")
            print(f"  GPU Max Used: {mem_info['gpu']['max_allocated']:.1f} MB")
    
    async def initialize_models(self):
        """Инициализация моделей с мониторингом"""
        print("🧠 Инициализация локальных AI-моделей на CUDA...")
        
        self.print_memory_status("До инициализации")
        
        # Инициализируем текстовый анализатор
        print("📝 Загрузка текстового анализатора...")
        start_time = time.time()
        self.text_analyzer = LocalTextAnalyzer()
        text_load_time = time.time() - start_time
        
        self.print_memory_status("После загрузки текстового анализатора")
        print(f"⏱️ Время загрузки: {text_load_time:.2f} сек")
        
        # Инициализируем голосовой анализатор
        print("\n🎤 Загрузка голосового анализатора...")
        start_time = time.time()
        self.voice_analyzer = LocalVoiceAnalyzer()
        voice_load_time = time.time() - start_time
        
        self.print_memory_status("После загрузки голосового анализатора")
        print(f"⏱️ Время загрузки: {voice_load_time:.2f} сек")
        
        return text_load_time, voice_load_time
    
    async def run_text_inference_benchmark(self):
        """Бенчмарк текстового inference"""
        print("\n🔥 CUDA TEXT INFERENCE BENCHMARK")
        print("=" * 50)
        
        # Тестовые тексты разной длины
        test_texts = [
            {
                'name': 'Короткий текст',
                'text': 'Привет! Как дела? Сегодня отличный день.',
                'expected_tokens': 20
            },
            {
                'name': 'Средний текст',
                'text': 'Сегодня я работаю над интересным проектом по машинному обучению. Использую локальные модели для анализа текста и голоса. Результаты впечатляют - высокая точность и скорость обработки на GPU.',
                'expected_tokens': 80
            },
            {
                'name': 'Длинный текст',
                'text': '''Разработка локальных AI-моделей для анализа текста представляет собой сложную техническую задачу. 
                Необходимо обеспечить высокую точность анализа тональности, определения эмоций и личностных черт, 
                при этом сохраняя приватность данных пользователя. Использование CUDA ускорения позволяет значительно 
                повысить производительность inference, особенно при обработке больших объемов текста. 
                Модели RuBERT, DistilRoBERTa и DeepPavlov показывают отличные результаты на русскоязычных данных.
                Важно правильно настроить токенизацию и обработку длинных последовательностей для избежания ошибок.''',
                'expected_tokens': 200
            },
            {
                'name': 'Технический текст',
                'text': '''**🔧 SPLINEGPT TOKENIZER: БЕНЧМАРК**
                У Rukallama свой BPE токенизатор с ёфикацией на основе SentencePiece. 
                Результаты: SplineGPT 16K vocab, fertility 1.99, STRR 54.4%, UNK 0.000%, Speed 62K/s.
                Это в 2.7× быстрее ruBERT/ruGPT-3 при компактном словаре в 7.5× меньше ruBERT.
                Обучение: 10K статей Russian Wikipedia, SentencePiece BPE, vocab 16K.''',
                'expected_tokens': 150
            }
        ]
        
        inference_results = []
        
        for i, test_case in enumerate(test_texts, 1):
            print(f"\n--- Тест {i}: {test_case['name']} ---")
            print(f"📝 Текст: {test_case['text'][:100]}...")
            print(f"🔢 Ожидаемые токены: ~{test_case['expected_tokens']}")
            
            # Очищаем кеш GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.print_memory_status(f"До inference {i}")
            
            # Запускаем inference
            start_time = time.time()
            
            try:
                result = await self.text_analyzer.analyze(test_case['text'])
                
                inference_time = time.time() - start_time
                
                if result.get('success'):
                    print(f"✅ Inference успешен")
                    print(f"⏱️ Время: {inference_time:.3f} сек")
                    print(f"🚀 Скорость: {test_case['expected_tokens']/inference_time:.1f} токенов/сек")
                    
                    # Результаты
                    sentiment = result.get('sentiment', {})
                    if sentiment:
                        print(f"📊 Тональность: {sentiment.get('label')} ({sentiment.get('confidence', 0)*100:.1f}%)")
                    
                    emotions = result.get('emotions', {})
                    if emotions:
                        top_emotion = max(emotions.items(), key=lambda x: x[1])
                        print(f"😊 Доминирующая эмоция: {top_emotion[0]} ({top_emotion[1]*100:.1f}%)")
                    
                    personality = result.get('personality', {})
                    if personality:
                        top_trait = max(personality.items(), key=lambda x: x[1])
                        print(f"👤 Выраженная черта: {top_trait[0]} ({top_trait[1]*100:.1f}%)")
                    
                    inference_results.append({
                        'test': test_case['name'],
                        'tokens': test_case['expected_tokens'],
                        'time': inference_time,
                        'tokens_per_sec': test_case['expected_tokens']/inference_time,
                        'success': True
                    })
                    
                else:
                    print(f"❌ Ошибка: {result.get('error')}")
                    inference_results.append({
                        'test': test_case['name'],
                        'success': False,
                        'error': result.get('error')
                    })
                
                self.print_memory_status(f"После inference {i}")
                
            except Exception as e:
                print(f"❌ Критическая ошибка: {e}")
                inference_results.append({
                    'test': test_case['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return inference_results
    
    async def run_voice_inference_test(self):
        """Тест голосового inference"""
        print("\n🎤 CUDA VOICE INFERENCE TEST")
        print("=" * 50)
        
        try:
            import tempfile
            import numpy as np
            import soundfile as sf
            
            # Создаем реалистичный аудио сигнал
            print("🎵 Генерация тестового аудио...")
            
            duration = 5  # секунд
            sample_rate = 16000
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Имитация человеческой речи
            base_freq = 150  # Основная частота голоса
            
            # Создаем сложный сигнал с гармониками
            signal = (0.4 * np.sin(2 * np.pi * base_freq * t) +
                     0.2 * np.sin(2 * np.pi * base_freq * 2 * t) +
                     0.1 * np.sin(2 * np.pi * base_freq * 3 * t) +
                     0.05 * np.sin(2 * np.pi * base_freq * 4 * t))
            
            # Добавляем интонационную модуляцию
            modulation = 1 + 0.3 * np.sin(2 * np.pi * 0.5 * t) * np.sin(2 * np.pi * 2 * t)
            signal *= modulation
            
            # Добавляем реалистичный шум
            noise = 0.02 * np.random.randn(len(t))
            signal += noise
            
            # Нормализуем
            signal = signal / np.max(np.abs(signal)) * 0.7
            
            # Сохраняем
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                sf.write(temp_file.name, signal, sample_rate)
                temp_path = temp_file.name
            
            print(f"✅ Аудио создано: {duration} сек, {sample_rate} Hz")
            
            # Мониторинг памяти
            self.print_memory_status("До голосового inference")
            
            # Создаем мок файла
            class MockVoiceFile:
                def __init__(self, path):
                    self.path = path
                
                async def download_to_drive(self, destination):
                    import shutil
                    shutil.copy2(self.path, destination)
            
            mock_file = MockVoiceFile(temp_path)
            
            # Запускаем анализ
            print("🔥 Запуск CUDA voice inference...")
            start_time = time.time()
            
            result = await self.voice_analyzer.analyze(mock_file, duration)
            
            inference_time = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ Voice inference успешен")
                print(f"⏱️ Время: {inference_time:.3f} сек")
                print(f"🚀 Скорость: {duration/inference_time:.1f}x реального времени")
                
                # Результаты
                audio_features = result.get('audio_features', {})
                if audio_features:
                    interpretation = audio_features.get('interpretation', {})
                    print("🔊 Аудио характеристики:")
                    for key, value in list(interpretation.items())[:4]:
                        print(f"  • {key}: {value}")
                
                transcription = result.get('transcription_analysis', {}).get('transcription', '')
                if transcription:
                    print(f"📝 Транскрипция: {transcription[:100]}...")
                else:
                    print("📝 Транскрипция: (синтетический сигнал)")
                
                self.print_memory_status("После голосового inference")
                
                # Удаляем временный файл
                os.unlink(temp_path)
                
                return {
                    'success': True,
                    'duration': duration,
                    'inference_time': inference_time,
                    'realtime_factor': duration/inference_time
                }
            else:
                print(f"❌ Ошибка: {result.get('error')}")
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            print(f"❌ Критическая ошибка голосового теста: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_performance_report(self, text_results, voice_result, load_times):
        """Генерация отчета производительности"""
        print("\n📊 CUDA PERFORMANCE REPORT")
        print("=" * 60)
        
        # Общая информация
        print(f"🎮 GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
        print(f"🔥 CUDA Version: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
        print(f"🧠 PyTorch: {torch.__version__}")
        
        # Время загрузки моделей
        print(f"\n⏱️ ЗАГРУЗКА МОДЕЛЕЙ:")
        print(f"  • Текстовый анализатор: {load_times[0]:.2f} сек")
        print(f"  • Голосовой анализатор: {load_times[1]:.2f} сек")
        print(f"  • Общее время загрузки: {sum(load_times):.2f} сек")
        
        # Результаты текстового inference
        print(f"\n📝 ТЕКСТОВЫЙ INFERENCE:")
        successful_text = [r for r in text_results if r.get('success')]
        
        if successful_text:
            avg_time = sum(r['time'] for r in successful_text) / len(successful_text)
            avg_speed = sum(r['tokens_per_sec'] for r in successful_text) / len(successful_text)
            
            print(f"  • Успешных тестов: {len(successful_text)}/{len(text_results)}")
            print(f"  • Среднее время: {avg_time:.3f} сек")
            print(f"  • Средняя скорость: {avg_speed:.1f} токенов/сек")
            
            print(f"\n  Детали по тестам:")
            for result in successful_text:
                print(f"    {result['test']}: {result['time']:.3f}с ({result['tokens_per_sec']:.1f} tok/s)")
        
        # Результаты голосового inference
        print(f"\n🎤 ГОЛОСОВОЙ INFERENCE:")
        if voice_result.get('success'):
            print(f"  • Статус: ✅ Успешно")
            print(f"  • Время обработки: {voice_result['inference_time']:.3f} сек")
            print(f"  • Скорость: {voice_result['realtime_factor']:.1f}x реального времени")
        else:
            print(f"  • Статус: ❌ Ошибка - {voice_result.get('error', 'Unknown')}")
        
        # Финальная оценка памяти
        final_memory = self.get_memory_info()
        print(f"\n💾 ФИНАЛЬНОЕ ИСПОЛЬЗОВАНИЕ ПАМЯТИ:")
        print(f"  • RAM: {final_memory['ram_mb']:.1f} MB ({final_memory['ram_mb']/1024:.2f} GB)")
        
        if final_memory['gpu']:
            gpu_total = final_memory['gpu']['allocated'] + final_memory['gpu']['cached']
            print(f"  • GPU Memory: {gpu_total:.1f} MB ({gpu_total/1024:.2f} GB)")
            print(f"    - Allocated: {final_memory['gpu']['allocated']:.1f} MB")
            print(f"    - Cached: {final_memory['gpu']['cached']:.1f} MB")
        
        # Общая оценка
        text_success_rate = len(successful_text) / len(text_results) if text_results else 0
        voice_success = voice_result.get('success', False)
        
        overall_score = (text_success_rate + (1 if voice_success else 0)) / 2
        
        print(f"\n🏆 ОБЩАЯ ОЦЕНКА:")
        print(f"  • Текстовый анализ: {text_success_rate*100:.0f}% успешность")
        print(f"  • Голосовой анализ: {'✅' if voice_success else '❌'}")
        print(f"  • Общий балл: {overall_score*100:.0f}%")
        
        if overall_score >= 0.8:
            print(f"  • Статус: 🎉 ОТЛИЧНО - Готов к продакшену!")
        elif overall_score >= 0.6:
            print(f"  • Статус: ✅ ХОРОШО - Требует минимальных доработок")
        else:
            print(f"  • Статус: ⚠️ ТРЕБУЕТ УЛУЧШЕНИЙ")


async def main():
    """Главная функция реального CUDA тестирования"""
    print("🔥 РЕАЛЬНЫЙ CUDA INFERENCE ТЕСТ")
    print("🔮 Oracul Local AI Models - Performance Benchmark")
    print("=" * 60)
    
    monitor = CUDAInferenceMonitor()
    
    try:
        # Проверяем CUDA
        if not torch.cuda.is_available():
            print("❌ CUDA недоступна! Тест невозможен.")
            return
        
        print(f"✅ CUDA доступна")
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        print(f"🔥 CUDA Version: {torch.version.cuda}")
        
        # Инициализация моделей
        load_times = await monitor.initialize_models()
        
        # Текстовый inference бенчмарк
        text_results = await monitor.run_text_inference_benchmark()
        
        # Голосовой inference тест
        voice_result = await monitor.run_voice_inference_test()
        
        # Генерация отчета
        monitor.generate_performance_report(text_results, voice_result, load_times)
        
        print(f"\n🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print(f"Все данные о производительности CUDA inference получены.")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
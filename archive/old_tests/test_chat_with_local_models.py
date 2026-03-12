#!/usr/bin/env python3
"""
Тест локальных моделей на данных из существующих анализов
"""

import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / 'oracul-bot'))

from analyzers.local_text_analyzer import LocalTextAnalyzer
from analyzers.local_voice_analyzer import LocalVoiceAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalModelsTester:
    """Тестер локальных моделей на реальных данных"""
    
    def __init__(self):
        self.text_analyzer = None
        self.voice_analyzer = None
    
    async def initialize(self):
        """Инициализация анализаторов"""
        try:
            logger.info("🧠 Инициализация локальных AI-моделей...")
            self.text_analyzer = LocalTextAnalyzer()
            self.voice_analyzer = LocalVoiceAnalyzer()
            logger.info("✅ Локальные анализаторы готовы")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    def load_existing_analysis_data(self):
        """Загрузка данных из существующих анализов"""
        try:
            # Ищем файлы анализов
            analysis_files = []
            analysis_dir = Path("analysis")
            
            if analysis_dir.exists():
                for file in analysis_dir.glob("*.json"):
                    if "1637334" in file.name or "message_" in file.name:
                        analysis_files.append(file)
            
            logger.info(f"📁 Найдено файлов анализа: {len(analysis_files)}")
            
            # Загружаем данные
            all_data = []
            for file in analysis_files[:3]:  # Берем первые 3 файла
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_data.append({
                            'file': file.name,
                            'data': data
                        })
                        logger.info(f"✅ Загружен: {file.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка загрузки {file.name}: {e}")
            
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных: {e}")
            return []
    
    def extract_text_messages(self, data_files):
        """Извлечение текстовых сообщений из данных"""
        try:
            text_messages = []
            
            for file_info in data_files:
                data = file_info['data']
                
                # Разные форматы данных
                if 'messages' in data:
                    messages = data['messages']
                elif 'analysis' in data:
                    messages = data.get('analysis', {}).get('messages', [])
                else:
                    messages = []
                
                for msg in messages:
                    if isinstance(msg, dict):
                        text = msg.get('text') or msg.get('message') or msg.get('content')
                        if text and len(text.strip()) > 10:
                            text_messages.append({
                                'text': text,
                                'source': file_info['file'],
                                'id': msg.get('id', 'unknown')
                            })
            
            logger.info(f"📝 Извлечено текстовых сообщений: {len(text_messages)}")
            return text_messages[:20]  # Ограничиваем для теста
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения текстов: {e}")
            return []
    
    async def analyze_texts_with_local_models(self, text_messages):
        """Анализ текстов локальными моделями"""
        try:
            logger.info("🧠 Анализ текстов локальными моделями...")
            
            if not text_messages:
                # Создаем тестовые сообщения
                text_messages = [
                    {'text': 'Привет! Как дела? Сегодня отличный день для работы над проектом.', 'source': 'test', 'id': 'test1'},
                    {'text': 'Устал от работы, много задач накопилось. Нужно отдохнуть.', 'source': 'test', 'id': 'test2'},
                    {'text': 'Интересная идея с использованием KAN архитектуры. Стоит попробовать.', 'source': 'test', 'id': 'test3'},
                    {'text': 'Модель показывает хорошие результаты на валидации. Loss снижается стабильно.', 'source': 'test', 'id': 'test4'},
                    {'text': 'Завтра планирую запустить новый эксперимент с большим датасетом.', 'source': 'test', 'id': 'test5'}
                ]
                logger.info("📝 Используем тестовые сообщения")
            
            analyses = []
            
            for i, msg in enumerate(text_messages[:10]):  # Анализируем первые 10
                logger.info(f"📊 Анализ сообщения {i+1}/{min(len(text_messages), 10)}")
                
                try:
                    result = await self.text_analyzer.analyze(msg['text'])
                    
                    if result.get('success'):
                        analyses.append({
                            'message_id': msg['id'],
                            'source': msg['source'],
                            'text_preview': msg['text'][:100] + '...' if len(msg['text']) > 100 else msg['text'],
                            'analysis': result
                        })
                        
                        # Показываем результат
                        sentiment = result.get('sentiment', {})
                        emotions = result.get('emotions', {})
                        
                        print(f"\n--- Сообщение {i+1} ---")
                        print(f"Текст: {msg['text'][:80]}...")
                        if sentiment:
                            print(f"📊 Тональность: {sentiment.get('label', 'unknown')} ({sentiment.get('confidence', 0)*100:.1f}%)")
                        if emotions:
                            top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
                            emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions])
                            print(f"😊 Эмоции: {emotion_str}")
                        
                        recommendations = result.get('recommendations', [])
                        if recommendations:
                            print(f"💡 Наблюдения: {'; '.join(recommendations[:2])}")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка анализа сообщения {i+1}: {e}")
                    continue
            
            return analyses
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа текстов: {e}")
            return []
    
    async def test_voice_analysis_capabilities(self):
        """Тест возможностей анализа голоса"""
        try:
            logger.info("🎤 Тест возможностей анализа голоса...")
            
            # Создаем тестовый аудио файл
            import tempfile
            import numpy as np
            import soundfile as sf
            
            # Генерируем тестовый сигнал
            duration = 3  # секунды
            sample_rate = 16000
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Создаем сложный сигнал (имитация речи)
            frequency1 = 200  # Основная частота
            frequency2 = 400  # Гармоника
            
            signal = (0.3 * np.sin(2 * np.pi * frequency1 * t) + 
                     0.2 * np.sin(2 * np.pi * frequency2 * t) +
                     0.1 * np.random.randn(len(t)))  # Шум
            
            # Добавляем модуляцию (имитация интонации)
            modulation = 1 + 0.3 * np.sin(2 * np.pi * 0.5 * t)
            signal *= modulation
            
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                sf.write(temp_file.name, signal, sample_rate)
                temp_path = temp_file.name
            
            # Создаем мок объект
            class MockVoiceFile:
                def __init__(self, path):
                    self.path = path
                
                async def download_to_drive(self, destination):
                    import shutil
                    shutil.copy2(self.path, destination)
            
            mock_file = MockVoiceFile(temp_path)
            
            # Анализируем
            result = await self.voice_analyzer.analyze(mock_file, duration)
            
            print(f"\n🎤 РЕЗУЛЬТАТЫ АНАЛИЗА ГОЛОСА:")
            
            if result.get('success'):
                print("✅ Анализ голоса успешен")
                
                # Аудио характеристики
                audio_features = result.get('audio_features', {})
                if audio_features:
                    interpretation = audio_features.get('interpretation', {})
                    print(f"🔊 Аудио характеристики:")
                    for key, value in interpretation.items():
                        print(f"  • {key}: {value}")
                
                # Рекомендации
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"💡 Наблюдения: {'; '.join(recommendations)}")
            else:
                print(f"❌ Ошибка анализа голоса: {result.get('error')}")
            
            # Удаляем временный файл
            os.unlink(temp_path)
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"❌ Ошибка теста голоса: {e}")
            return False
    
    def generate_comprehensive_summary(self, text_analyses, voice_test_result):
        """Генерация комплексного резюме"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'text_analysis': {
                    'messages_analyzed': len(text_analyses),
                    'success_rate': len([a for a in text_analyses if a.get('analysis', {}).get('success')]) / max(len(text_analyses), 1),
                    'insights': []
                },
                'voice_analysis': {
                    'test_passed': voice_test_result,
                    'capabilities': ['whisper_transcription', 'librosa_features', 'emotion_detection']
                },
                'overall_assessment': {}
            }
            
            # Анализируем результаты текста
            if text_analyses:
                sentiments = []
                emotions_total = {}
                
                for analysis in text_analyses:
                    result = analysis.get('analysis', {})
                    
                    # Собираем тональности
                    sentiment = result.get('sentiment', {})
                    if sentiment.get('label'):
                        sentiments.append(sentiment['label'])
                    
                    # Собираем эмоции
                    emotions = result.get('emotions', {})
                    for emotion, score in emotions.items():
                        emotions_total[emotion] = emotions_total.get(emotion, 0) + score
                
                # Статистика тональности
                if sentiments:
                    sentiment_counts = {}
                    for s in sentiments:
                        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
                    
                    dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])
                    summary['text_analysis']['dominant_sentiment'] = {
                        'label': dominant_sentiment[0],
                        'frequency': dominant_sentiment[1] / len(sentiments)
                    }
                
                # Топ эмоции
                if emotions_total:
                    avg_emotions = {k: v/len(text_analyses) for k, v in emotions_total.items()}
                    top_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)[:3]
                    summary['text_analysis']['top_emotions'] = top_emotions
            
            # Общая оценка
            text_score = summary['text_analysis']['success_rate']
            voice_score = 1.0 if voice_test_result else 0.0
            
            overall_score = (text_score + voice_score) / 2
            
            summary['overall_assessment'] = {
                'score': overall_score,
                'text_analysis_ready': text_score > 0.8,
                'voice_analysis_ready': voice_test_result,
                'production_ready': overall_score > 0.8
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации резюме: {e}")
            return {}


async def main():
    """Главная функция тестирования"""
    print("🔮 ТЕСТ ЛОКАЛЬНЫХ AI-МОДЕЛЕЙ НА РЕАЛЬНЫХ ДАННЫХ")
    print("=" * 60)
    
    tester = LocalModelsTester()
    
    try:
        # Инициализация
        if not await tester.initialize():
            print("❌ Ошибка инициализации")
            return
        
        # Загрузка данных
        print("\n📁 ЭТАП 1: Загрузка существующих данных")
        data_files = tester.load_existing_analysis_data()
        
        if data_files:
            print(f"✅ Загружено файлов: {len(data_files)}")
            for file_info in data_files:
                print(f"  • {file_info['file']}")
        else:
            print("⚠️ Существующие данные не найдены, используем тестовые")
        
        # Извлечение текстов
        print("\n📝 ЭТАП 2: Извлечение текстовых сообщений")
        text_messages = tester.extract_text_messages(data_files)
        print(f"✅ Извлечено сообщений: {len(text_messages)}")
        
        # Анализ текстов
        print("\n🧠 ЭТАП 3: Анализ текстов локальными моделями")
        text_analyses = await tester.analyze_texts_with_local_models(text_messages)
        print(f"✅ Проанализировано: {len(text_analyses)} сообщений")
        
        # Тест голосового анализа
        print("\n🎤 ЭТАП 4: Тест голосового анализа")
        voice_result = await tester.test_voice_analysis_capabilities()
        
        # Комплексное резюме
        print("\n📊 ЭТАП 5: Генерация комплексного резюме")
        summary = tester.generate_comprehensive_summary(text_analyses, voice_result)
        
        if summary:
            print("✅ Резюме сгенерировано")
            
            # Показываем ключевые результаты
            text_analysis = summary.get('text_analysis', {})
            voice_analysis = summary.get('voice_analysis', {})
            overall = summary.get('overall_assessment', {})
            
            print(f"\n📈 КЛЮЧЕВЫЕ РЕЗУЛЬТАТЫ:")
            print(f"  • Проанализировано сообщений: {text_analysis.get('messages_analyzed', 0)}")
            print(f"  • Успешность анализа текста: {text_analysis.get('success_rate', 0)*100:.1f}%")
            print(f"  • Голосовой анализ: {'✅ Работает' if voice_analysis.get('test_passed') else '❌ Ошибка'}")
            
            # Доминирующая тональность
            dominant = text_analysis.get('dominant_sentiment', {})
            if dominant:
                print(f"  • Доминирующая тональность: {dominant.get('label', 'unknown')} ({dominant.get('frequency', 0)*100:.1f}%)")
            
            # Топ эмоции
            top_emotions = text_analysis.get('top_emotions', [])
            if top_emotions:
                emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions[:2]])
                print(f"  • Основные эмоции: {emotion_str}")
            
            # Общая оценка
            score = overall.get('score', 0)
            print(f"  • Общая оценка системы: {score*100:.1f}%")
            print(f"  • Готовность к продакшену: {'✅ Да' if overall.get('production_ready') else '❌ Требует доработки'}")
            
            # Сохраняем резюме
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis/local_models_test_summary_{timestamp}.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Резюме сохранено: {filename}")
        
        # Итоги
        print("\n" + "=" * 60)
        print("🎯 ИТОГИ ТЕСТИРОВАНИЯ:")
        
        success_count = 0
        total_tests = 4
        
        if len(text_analyses) > 0:
            print("✅ Анализ текста: Успешно")
            success_count += 1
        else:
            print("❌ Анализ текста: Ошибка")
        
        if voice_result:
            print("✅ Анализ голоса: Успешно")
            success_count += 1
        else:
            print("❌ Анализ голоса: Ошибка")
        
        if summary:
            print("✅ Генерация отчета: Успешно")
            success_count += 1
        else:
            print("❌ Генерация отчета: Ошибка")
        
        if summary and summary.get('overall_assessment', {}).get('production_ready'):
            print("✅ Готовность к продакшену: Да")
            success_count += 1
        else:
            print("❌ Готовность к продакшену: Требует доработки")
        
        print(f"\n🏆 Результат: {success_count}/{total_tests} тестов пройдено")
        
        if success_count == total_tests:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Локальные AI-модели полностью готовы!")
        elif success_count >= 3:
            print("✅ Основные тесты пройдены. Система готова к использованию.")
        else:
            print("⚠️ Требуется доработка. Проверьте настройки и зависимости.")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
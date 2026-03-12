#!/usr/bin/env python3
"""
Полный анализ реального чата с использованием локальных AI-моделей
Тестирование всех модальностей на чате ID 1637334
"""

import asyncio
import sys
import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import tempfile

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'oracul-bot'))

from telethon import TelegramClient
from telethon.sessions import StringSession

# Локальные анализаторы
sys.path.insert(0, str(Path(__file__).parent / 'oracul-bot'))
from analyzers.local_text_analyzer import LocalTextAnalyzer
from analyzers.local_voice_analyzer import LocalVoiceAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
CHAT_ID = 1637334
MAX_MESSAGES = 50  # Ограничиваем для теста
VOICE_ANALYSIS_LIMIT = 5  # Максимум голосовых для анализа


class RealChatAnalyzer:
    """Анализатор реального чата с локальными моделями"""
    
    def __init__(self):
        self.client = None
        self.text_analyzer = None
        self.voice_analyzer = None
        self.session_file = "oracul.session"
        
    async def initialize(self):
        """Инициализация клиента и анализаторов"""
        try:
            # Инициализируем Telegram клиент
            if os.path.exists(self.session_file):
                logger.info("📱 Загружаем существующую сессию Telegram...")
                try:
                    with open(self.session_file, 'r', encoding='utf-8') as f:
                        session_string = f.read().strip()
                except UnicodeDecodeError:
                    # Пробуем другие кодировки
                    try:
                        with open(self.session_file, 'r', encoding='latin-1') as f:
                            session_string = f.read().strip()
                    except:
                        with open(self.session_file, 'rb') as f:
                            session_string = f.read().decode('utf-8', errors='ignore').strip()
                
                self.client = TelegramClient(
                    StringSession(session_string),
                    api_id=None,  # Будет взято из сессии
                    api_hash=None
                )
            else:
                logger.error("❌ Файл сессии не найден!")
                return False
            
            await self.client.start()
            logger.info("✅ Telegram клиент подключен")
            
            # Инициализируем локальные анализаторы
            logger.info("🧠 Инициализация локальных AI-моделей...")
            self.text_analyzer = LocalTextAnalyzer()
            self.voice_analyzer = LocalVoiceAnalyzer()
            logger.info("✅ Локальные анализаторы готовы")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def collect_chat_data(self) -> Dict:
        """Сбор данных из чата"""
        try:
            logger.info(f"📥 Сбор данных из чата {CHAT_ID}...")
            
            # Получаем информацию о чате
            chat = await self.client.get_entity(CHAT_ID)
            logger.info(f"💬 Чат: {getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))}")
            
            # Собираем сообщения
            messages = []
            text_messages = []
            voice_messages = []
            
            async for message in self.client.iter_messages(chat, limit=MAX_MESSAGES):
                msg_data = {
                    'id': message.id,
                    'date': message.date,
                    'text': message.text,
                    'from_id': getattr(message.from_id, 'user_id', None) if message.from_id else None,
                    'media_type': None,
                    'voice_duration': None
                }
                
                # Проверяем тип медиа
                if message.media:
                    if hasattr(message.media, 'document'):
                        doc = message.media.document
                        if doc.mime_type == 'audio/ogg':
                            msg_data['media_type'] = 'voice'
                            # Ищем атрибут длительности
                            for attr in doc.attributes:
                                if hasattr(attr, 'duration'):
                                    msg_data['voice_duration'] = attr.duration
                                    break
                            voice_messages.append((message, msg_data))
                
                if message.text:
                    text_messages.append(msg_data)
                
                messages.append(msg_data)
            
            logger.info(f"📊 Собрано сообщений:")
            logger.info(f"  • Всего: {len(messages)}")
            logger.info(f"  • Текстовых: {len(text_messages)}")
            logger.info(f"  • Голосовых: {len(voice_messages)}")
            
            return {
                'chat_info': {
                    'id': CHAT_ID,
                    'title': getattr(chat, 'title', getattr(chat, 'first_name', 'Private Chat')),
                    'type': 'private' if hasattr(chat, 'first_name') else 'group'
                },
                'messages': messages,
                'text_messages': text_messages,
                'voice_messages': voice_messages[:VOICE_ANALYSIS_LIMIT]  # Ограничиваем
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка сбора данных: {e}")
            return {}
    
    async def analyze_text_messages(self, text_messages: List[Dict]) -> Dict:
        """Анализ текстовых сообщений"""
        try:
            logger.info("🧠 Анализ текстовых сообщений...")
            
            if not text_messages:
                return {'success': False, 'error': 'Нет текстовых сообщений'}
            
            # Берем последние сообщения для анализа
            recent_messages = text_messages[:10]
            
            analyses = []
            combined_text = ""
            
            for i, msg in enumerate(recent_messages):
                if not msg['text'] or len(msg['text'].strip()) < 5:
                    continue
                
                logger.info(f"📝 Анализ сообщения {i+1}/{len(recent_messages)}")
                
                # Анализируем отдельное сообщение
                result = await self.text_analyzer.analyze(msg['text'])
                
                if result.get('success'):
                    analyses.append({
                        'message_id': msg['id'],
                        'text': msg['text'][:100] + '...' if len(msg['text']) > 100 else msg['text'],
                        'date': msg['date'].isoformat(),
                        'analysis': result
                    })
                    
                    combined_text += msg['text'] + " "
            
            # Общий анализ всех сообщений
            logger.info("🔍 Комплексный анализ всех текстов...")
            combined_analysis = None
            if combined_text.strip():
                combined_analysis = await self.text_analyzer.analyze(combined_text[:2000])
            
            return {
                'success': True,
                'individual_analyses': analyses,
                'combined_analysis': combined_analysis,
                'summary': self._generate_text_summary(analyses, combined_analysis)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа текста: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_voice_messages(self, voice_messages: List[tuple]) -> Dict:
        """Анализ голосовых сообщений"""
        try:
            logger.info("🎤 Анализ голосовых сообщений...")
            
            if not voice_messages:
                return {'success': False, 'error': 'Нет голосовых сообщений'}
            
            analyses = []
            
            for i, (message, msg_data) in enumerate(voice_messages):
                logger.info(f"🎙️ Анализ голосового {i+1}/{len(voice_messages)}")
                
                try:
                    # Скачиваем голосовое сообщение
                    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                        await message.download_media(temp_file.name)
                        temp_path = temp_file.name
                    
                    # Создаем мок объект для анализатора
                    class MockVoiceFile:
                        def __init__(self, path):
                            self.path = path
                        
                        async def download_to_drive(self, destination):
                            import shutil
                            shutil.copy2(self.path, destination)
                    
                    mock_file = MockVoiceFile(temp_path)
                    duration = msg_data.get('voice_duration', 10)  # Дефолт 10 сек
                    
                    # Анализируем
                    result = await self.voice_analyzer.analyze(mock_file, duration)
                    
                    if result.get('success'):
                        analyses.append({
                            'message_id': msg_data['id'],
                            'duration': duration,
                            'date': msg_data['date'].isoformat(),
                            'analysis': result
                        })
                        
                        logger.info(f"✅ Голосовое {i+1} проанализировано")
                    else:
                        logger.warning(f"⚠️ Ошибка анализа голосового {i+1}: {result.get('error')}")
                    
                    # Удаляем временный файл
                    os.unlink(temp_path)
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки голосового {i+1}: {e}")
                    continue
            
            return {
                'success': True,
                'analyses': analyses,
                'summary': self._generate_voice_summary(analyses)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа голоса: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_text_summary(self, analyses: List[Dict], combined_analysis: Optional[Dict]) -> Dict:
        """Генерация резюме текстового анализа"""
        try:
            if not analyses:
                return {}
            
            # Собираем статистику
            sentiments = []
            emotions_total = {}
            personality_total = {}
            
            for analysis in analyses:
                result = analysis['analysis']
                
                # Тональность
                sentiment = result.get('sentiment', {})
                if sentiment.get('label'):
                    sentiments.append(sentiment['label'])
                
                # Эмоции
                emotions = result.get('emotions', {})
                for emotion, score in emotions.items():
                    emotions_total[emotion] = emotions_total.get(emotion, 0) + score
                
                # Личность
                personality = result.get('personality', {})
                for trait, score in personality.items():
                    personality_total[trait] = personality_total.get(trait, 0) + score
            
            # Вычисляем средние значения
            num_analyses = len(analyses)
            
            # Доминирующая тональность
            sentiment_counts = {}
            for s in sentiments:
                sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
            
            dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1]) if sentiment_counts else ('neutral', 0)
            
            # Топ эмоции
            avg_emotions = {k: v/num_analyses for k, v in emotions_total.items()}
            top_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Топ черты личности
            avg_personality = {k: v/num_analyses for k, v in personality_total.items()}
            top_traits = sorted(avg_personality.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'messages_analyzed': num_analyses,
                'dominant_sentiment': {
                    'label': dominant_sentiment[0],
                    'frequency': dominant_sentiment[1] / num_analyses
                },
                'top_emotions': top_emotions,
                'top_personality_traits': top_traits,
                'combined_analysis_available': combined_analysis is not None
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации резюме текста: {e}")
            return {}
    
    def _generate_voice_summary(self, analyses: List[Dict]) -> Dict:
        """Генерация резюме голосового анализа"""
        try:
            if not analyses:
                return {}
            
            total_duration = sum(a['duration'] for a in analyses)
            
            # Собираем характеристики
            audio_features = []
            transcriptions = []
            
            for analysis in analyses:
                result = analysis['analysis']
                
                # Аудио характеристики
                audio_feat = result.get('audio_features', {})
                if audio_feat:
                    audio_features.append(audio_feat.get('interpretation', {}))
                
                # Транскрипции
                trans_analysis = result.get('transcription_analysis', {})
                transcription = trans_analysis.get('transcription', '')
                if transcription and len(transcription.strip()) > 5:
                    transcriptions.append(transcription)
            
            # Анализируем общие паттерны
            common_patterns = {}
            if audio_features:
                for feature in audio_features:
                    for key, value in feature.items():
                        if key not in common_patterns:
                            common_patterns[key] = []
                        common_patterns[key].append(value)
                
                # Находим наиболее частые характеристики
                dominant_patterns = {}
                for key, values in common_patterns.items():
                    if values:
                        # Находим наиболее частое значение
                        value_counts = {}
                        for v in values:
                            value_counts[v] = value_counts.get(v, 0) + 1
                        dominant_patterns[key] = max(value_counts.items(), key=lambda x: x[1])[0]
            
            return {
                'voice_messages_analyzed': len(analyses),
                'total_duration': total_duration,
                'transcriptions_found': len(transcriptions),
                'dominant_audio_patterns': dominant_patterns,
                'sample_transcriptions': transcriptions[:3]  # Первые 3
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации резюме голоса: {e}")
            return {}
    
    async def generate_comprehensive_report(self, chat_data: Dict, text_analysis: Dict, voice_analysis: Dict) -> Dict:
        """Генерация комплексного отчета"""
        try:
            logger.info("📊 Генерация комплексного отчета...")
            
            report = {
                'analysis_timestamp': datetime.now().isoformat(),
                'chat_info': chat_data.get('chat_info', {}),
                'data_summary': {
                    'total_messages': len(chat_data.get('messages', [])),
                    'text_messages': len(chat_data.get('text_messages', [])),
                    'voice_messages': len(chat_data.get('voice_messages', []))
                },
                'text_analysis': text_analysis,
                'voice_analysis': voice_analysis,
                'insights': []
            }
            
            # Генерируем инсайты
            insights = []
            
            # Инсайты по тексту
            if text_analysis.get('success'):
                text_summary = text_analysis.get('summary', {})
                if text_summary:
                    dominant_sentiment = text_summary.get('dominant_sentiment', {})
                    if dominant_sentiment.get('label'):
                        insights.append(f"Доминирующая тональность: {dominant_sentiment['label']} ({dominant_sentiment.get('frequency', 0)*100:.1f}% сообщений)")
                    
                    top_emotions = text_summary.get('top_emotions', [])
                    if top_emotions:
                        emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions[:2]])
                        insights.append(f"Основные эмоции: {emotion_str}")
                    
                    top_traits = text_summary.get('top_personality_traits', [])
                    if top_traits:
                        trait_str = ', '.join([f"{t}: {s*100:.1f}%" for t, s in top_traits[:2]])
                        insights.append(f"Выраженные черты личности: {trait_str}")
            
            # Инсайты по голосу
            if voice_analysis.get('success'):
                voice_summary = voice_analysis.get('summary', {})
                if voice_summary:
                    total_duration = voice_summary.get('total_duration', 0)
                    if total_duration > 0:
                        insights.append(f"Общая длительность голосовых: {total_duration} секунд")
                    
                    patterns = voice_summary.get('dominant_audio_patterns', {})
                    if patterns:
                        pattern_insights = []
                        for key, value in patterns.items():
                            pattern_insights.append(f"{key}: {value}")
                        if pattern_insights:
                            insights.append(f"Голосовые характеристики: {'; '.join(pattern_insights[:3])}")
            
            # Кросс-модальные инсайты
            if text_analysis.get('success') and voice_analysis.get('success'):
                insights.append("Проведен мультимодальный анализ текста и голоса")
            
            report['insights'] = insights
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчета: {e}")
            return {}
    
    async def save_report(self, report: Dict, filename: str = None):
        """Сохранение отчета"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis/chat_{CHAT_ID}_full_analysis_{timestamp}.json"
            
            # Создаем директорию если нужно
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 Отчет сохранен: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения отчета: {e}")
            return None
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if self.client:
            await self.client.disconnect()


async def main():
    """Главная функция тестирования"""
    print("🔮 ПОЛНЫЙ АНАЛИЗ РЕАЛЬНОГО ЧАТА С ЛОКАЛЬНЫМИ AI-МОДЕЛЯМИ")
    print("=" * 70)
    print(f"📱 Чат ID: {CHAT_ID}")
    print(f"📊 Максимум сообщений: {MAX_MESSAGES}")
    print(f"🎤 Максимум голосовых: {VOICE_ANALYSIS_LIMIT}")
    print("=" * 70)
    
    analyzer = RealChatAnalyzer()
    
    try:
        # Инициализация
        if not await analyzer.initialize():
            print("❌ Ошибка инициализации")
            return
        
        # Сбор данных
        print("\n📥 ЭТАП 1: Сбор данных из чата")
        chat_data = await analyzer.collect_chat_data()
        
        if not chat_data:
            print("❌ Не удалось собрать данные чата")
            return
        
        print(f"✅ Данные собраны:")
        print(f"  • Всего сообщений: {len(chat_data.get('messages', []))}")
        print(f"  • Текстовых: {len(chat_data.get('text_messages', []))}")
        print(f"  • Голосовых: {len(chat_data.get('voice_messages', []))}")
        
        # Анализ текста
        print("\n🧠 ЭТАП 2: Анализ текстовых сообщений")
        text_analysis = await analyzer.analyze_text_messages(chat_data.get('text_messages', []))
        
        if text_analysis.get('success'):
            print("✅ Текстовый анализ завершен")
            summary = text_analysis.get('summary', {})
            if summary:
                print(f"  • Проанализировано сообщений: {summary.get('messages_analyzed', 0)}")
                dominant = summary.get('dominant_sentiment', {})
                if dominant:
                    print(f"  • Доминирующая тональность: {dominant.get('label', 'unknown')} ({dominant.get('frequency', 0)*100:.1f}%)")
        else:
            print(f"❌ Ошибка текстового анализа: {text_analysis.get('error')}")
        
        # Анализ голоса
        print("\n🎤 ЭТАП 3: Анализ голосовых сообщений")
        voice_analysis = await analyzer.analyze_voice_messages(chat_data.get('voice_messages', []))
        
        if voice_analysis.get('success'):
            print("✅ Голосовой анализ завершен")
            summary = voice_analysis.get('summary', {})
            if summary:
                print(f"  • Проанализировано голосовых: {summary.get('voice_messages_analyzed', 0)}")
                print(f"  • Общая длительность: {summary.get('total_duration', 0)} сек")
                print(f"  • Найдено транскрипций: {summary.get('transcriptions_found', 0)}")
        else:
            print(f"❌ Ошибка голосового анализа: {voice_analysis.get('error')}")
        
        # Комплексный отчет
        print("\n📊 ЭТАП 4: Генерация комплексного отчета")
        report = await analyzer.generate_comprehensive_report(chat_data, text_analysis, voice_analysis)
        
        if report:
            print("✅ Комплексный отчет сгенерирован")
            
            # Показываем ключевые инсайты
            insights = report.get('insights', [])
            if insights:
                print("\n💡 КЛЮЧЕВЫЕ ИНСАЙТЫ:")
                for i, insight in enumerate(insights, 1):
                    print(f"  {i}. {insight}")
            
            # Сохраняем отчет
            filename = await analyzer.save_report(report)
            if filename:
                print(f"\n💾 Отчет сохранен: {filename}")
        else:
            print("❌ Ошибка генерации отчета")
        
        # Итоги
        print("\n" + "=" * 70)
        print("📈 ИТОГИ ТЕСТИРОВАНИЯ:")
        
        success_count = 0
        total_tests = 3
        
        if chat_data:
            print("✅ Сбор данных: Успешно")
            success_count += 1
        else:
            print("❌ Сбор данных: Ошибка")
        
        if text_analysis.get('success'):
            print("✅ Анализ текста: Успешно")
            success_count += 1
        else:
            print("❌ Анализ текста: Ошибка")
        
        if voice_analysis.get('success'):
            print("✅ Анализ голоса: Успешно")
            success_count += 1
        else:
            print("❌ Анализ голоса: Ошибка")
        
        print(f"\n🎯 Результат: {success_count}/{total_tests} этапов успешно")
        
        if success_count == total_tests:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система полностью готова к работе.")
        elif success_count >= 2:
            print("✅ Основные функции работают. Система готова к использованию.")
        else:
            print("⚠️ Требуется доработка. Проверьте настройки.")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")
    
    finally:
        await analyzer.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
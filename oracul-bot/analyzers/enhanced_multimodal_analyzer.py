"""
Расширенный мультимодальный анализатор
Включает реальный голосовой анализ, временную динамику и большие объемы данных
"""

import logging
import asyncio
import os
import json
import tempfile
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

# Импортируем существующие анализаторы
from .local_text_analyzer import LocalTextAnalyzer
from .local_voice_analyzer import LocalVoiceAnalyzer

logger = logging.getLogger(__name__)


class EnhancedMultimodalAnalyzer:
    """Расширенный анализатор с поддержкой всех модальностей и временной динамики"""
    
    def __init__(self):
        self.text_analyzer = None
        self.voice_analyzer = None
        self.initialized = False
    
    async def initialize(self):
        """Инициализация всех анализаторов"""
        try:
            logger.info("🚀 Инициализация расширенного мультимодального анализатора...")
            
            # Инициализируем анализаторы
            self.text_analyzer = LocalTextAnalyzer()
            self.voice_analyzer = LocalVoiceAnalyzer()
            
            self.initialized = True
            logger.info("✅ Расширенный анализатор готов")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def analyze_large_dataset(self, messages: List[Dict], 
                                  max_messages: int = 200,
                                  use_modern: bool = True) -> Dict:
        """Анализ большого объема сообщений с батчевой обработкой"""
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"📊 Анализ большого датасета: {len(messages)} сообщений")
            
            # Ограничиваем количество для обработки
            messages_to_process = messages[:max_messages]
            
            # Разбиваем на батчи для эффективной обработки
            batch_size = 20
            batches = [messages_to_process[i:i + batch_size] 
                      for i in range(0, len(messages_to_process), batch_size)]
            
            all_analyses = []
            batch_summaries = []
            
            for i, batch in enumerate(batches, 1):
                logger.info(f"🔄 Обработка батча {i}/{len(batches)} ({len(batch)} сообщений)")
                
                batch_results = []
                for message in batch:
                    try:
                        if message.get('text'):
                            # Текстовый анализ
                            result = await self.text_analyzer.analyze(
                                message['text'], 
                                use_modern=use_modern
                            )
                            
                            if result.get('success'):
                                batch_results.append({
                                    'message_id': message.get('id'),
                                    'date': message.get('date'),
                                    'text': message['text'],
                                    'analysis': result,
                                    'type': 'text'
                                })
                        
                        elif message.get('voice_file'):
                            # Голосовой анализ
                            voice_result = await self._analyze_voice_message(message)
                            if voice_result.get('success'):
                                batch_results.append({
                                    'message_id': message.get('id'),
                                    'date': message.get('date'),
                                    'voice_duration': message.get('duration', 0),
                                    'analysis': voice_result,
                                    'type': 'voice'
                                })
                                
                    except Exception as e:
                        logger.error(f"Ошибка анализа сообщения {message.get('id')}: {e}")
                        continue
                
                all_analyses.extend(batch_results)
                
                # Создаем сводку по батчу
                batch_summary = self._create_batch_summary(batch_results, i)
                batch_summaries.append(batch_summary)
                
                # Небольшая пауза между батчами
                await asyncio.sleep(0.5)
            
            # Создаем общую сводку
            overall_summary = self._create_overall_summary(all_analyses, batch_summaries)
            
            return {
                'success': True,
                'total_processed': len(all_analyses),
                'batches_processed': len(batches),
                'analyses': all_analyses,
                'batch_summaries': batch_summaries,
                'overall_summary': overall_summary
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа большого датасета: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _analyze_voice_message(self, message: Dict) -> Dict:
        """Анализ голосового сообщения"""
        try:
            voice_file = message.get('voice_file')
            duration = message.get('duration', 10)
            
            if not voice_file:
                return {'success': False, 'error': 'No voice file provided'}
            
            # Анализируем голосовое сообщение
            result = await self.voice_analyzer.analyze(voice_file, duration)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка анализа голоса: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_batch_summary(self, batch_results: List[Dict], batch_num: int) -> Dict:
        """Создание сводки по батчу"""
        try:
            if not batch_results:
                return {'batch': batch_num, 'empty': True}
            
            # Анализ тональности в батче
            sentiments = []
            emotions = {}
            text_count = 0
            voice_count = 0
            
            for result in batch_results:
                if result['type'] == 'text':
                    text_count += 1
                    analysis = result['analysis']
                    
                    # Тональность
                    sentiment = analysis.get('sentiment', {})
                    if sentiment.get('label'):
                        sentiments.append(sentiment['label'])
                    
                    # Эмоции
                    result_emotions = analysis.get('emotions', {})
                    for emotion, score in result_emotions.items():
                        emotions[emotion] = emotions.get(emotion, 0) + score
                        
                elif result['type'] == 'voice':
                    voice_count += 1
            
            # Доминирующая тональность
            sentiment_counts = {}
            for s in sentiments:
                sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
            
            dominant_sentiment = None
            if sentiment_counts:
                dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])
            
            return {
                'batch': batch_num,
                'total_messages': len(batch_results),
                'text_messages': text_count,
                'voice_messages': voice_count,
                'dominant_sentiment': dominant_sentiment,
                'sentiment_distribution': sentiment_counts,
                'avg_emotions': {k: v/text_count for k, v in emotions.items()} if text_count > 0 else {}
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания сводки батча: {e}")
            return {'batch': batch_num, 'error': str(e)}
    
    def _create_overall_summary(self, all_analyses: List[Dict], batch_summaries: List[Dict]) -> Dict:
        """Создание общей сводки"""
        try:
            total_messages = len(all_analyses)
            text_messages = len([a for a in all_analyses if a['type'] == 'text'])
            voice_messages = len([a for a in all_analyses if a['type'] == 'voice'])
            
            # Общая статистика тональности
            all_sentiments = []
            all_emotions = {}
            
            for analysis in all_analyses:
                if analysis['type'] == 'text':
                    result = analysis['analysis']
                    
                    # Тональность
                    sentiment = result.get('sentiment', {})
                    if sentiment.get('label'):
                        all_sentiments.append(sentiment['label'])
                    
                    # Эмоции
                    emotions = result.get('emotions', {})
                    for emotion, score in emotions.items():
                        all_emotions[emotion] = all_emotions.get(emotion, 0) + score
            
            # Распределение тональности
            sentiment_distribution = {}
            for s in all_sentiments:
                sentiment_distribution[s] = sentiment_distribution.get(s, 0) + 1
            
            # Средние эмоции
            avg_emotions = {}
            if text_messages > 0:
                avg_emotions = {k: v/text_messages for k, v in all_emotions.items()}
            
            return {
                'total_messages': total_messages,
                'text_messages': text_messages,
                'voice_messages': voice_messages,
                'sentiment_distribution': sentiment_distribution,
                'avg_emotions': avg_emotions,
                'batches_processed': len(batch_summaries),
                'processing_efficiency': f"{total_messages}/{len(batch_summaries)*20:.1f}" if batch_summaries else "N/A"
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания общей сводки: {e}")
            return {'error': str(e)}
    
    async def analyze_temporal_dynamics(self, analyses: List[Dict], 
                                      time_window_hours: int = 24) -> Dict:
        """Анализ временной динамики эмоций и тональности"""
        try:
            logger.info(f"⏰ Анализ временной динамики (окно: {time_window_hours}ч)")
            
            if not analyses:
                return {'success': False, 'error': 'No analyses provided'}
            
            # Сортируем по времени
            sorted_analyses = sorted(analyses, key=lambda x: x.get('date', ''))
            
            # Группируем по временным окнам
            time_windows = self._create_time_windows(sorted_analyses, time_window_hours)
            
            # Анализируем динамику
            dynamics = {
                'time_windows': time_windows,
                'sentiment_trends': self._analyze_sentiment_trends(time_windows),
                'emotion_trends': self._analyze_emotion_trends(time_windows),
                'activity_patterns': self._analyze_activity_patterns(time_windows),
                'insights': []
            }
            
            # Генерируем инсайты
            dynamics['insights'] = self._generate_temporal_insights(dynamics)
            
            return {
                'success': True,
                'dynamics': dynamics
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа временной динамики: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_time_windows(self, analyses: List[Dict], window_hours: int) -> List[Dict]:
        """Создание временных окон"""
        try:
            if not analyses:
                return []
            
            windows = []
            current_window = []
            window_start = None
            
            for analysis in analyses:
                try:
                    # Парсим дату
                    date_str = analysis.get('date', '')
                    if isinstance(date_str, str):
                        msg_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        msg_time = date_str
                    
                    # Первое сообщение - начало окна
                    if window_start is None:
                        window_start = msg_time
                        current_window = [analysis]
                        continue
                    
                    # Проверяем, входит ли в текущее окно
                    time_diff = (msg_time - window_start).total_seconds() / 3600
                    
                    if time_diff <= window_hours:
                        current_window.append(analysis)
                    else:
                        # Закрываем текущее окно
                        if current_window:
                            windows.append({
                                'start_time': window_start,
                                'end_time': window_start + timedelta(hours=window_hours),
                                'messages': current_window,
                                'count': len(current_window)
                            })
                        
                        # Начинаем новое окно
                        window_start = msg_time
                        current_window = [analysis]
                        
                except Exception as e:
                    logger.error(f"Ошибка обработки времени: {e}")
                    continue
            
            # Добавляем последнее окно
            if current_window:
                windows.append({
                    'start_time': window_start,
                    'end_time': window_start + timedelta(hours=window_hours),
                    'messages': current_window,
                    'count': len(current_window)
                })
            
            return windows
            
        except Exception as e:
            logger.error(f"Ошибка создания временных окон: {e}")
            return []
    
    def _analyze_sentiment_trends(self, time_windows: List[Dict]) -> Dict:
        """Анализ трендов тональности"""
        try:
            trends = {
                'positive_trend': [],
                'negative_trend': [],
                'neutral_trend': [],
                'overall_trend': 'stable'
            }
            
            for window in time_windows:
                sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
                
                for msg in window['messages']:
                    if msg['type'] == 'text':
                        analysis = msg['analysis']
                        sentiment = analysis.get('sentiment', {})
                        label = sentiment.get('label', 'neutral')
                        sentiments[label] = sentiments.get(label, 0) + 1
                
                total = sum(sentiments.values())
                if total > 0:
                    trends['positive_trend'].append(sentiments['positive'] / total)
                    trends['negative_trend'].append(sentiments['negative'] / total)
                    trends['neutral_trend'].append(sentiments['neutral'] / total)
            
            # Определяем общий тренд
            if len(trends['positive_trend']) >= 2:
                if trends['positive_trend'][-1] > trends['positive_trend'][0]:
                    trends['overall_trend'] = 'improving'
                elif trends['positive_trend'][-1] < trends['positive_trend'][0]:
                    trends['overall_trend'] = 'declining'
            
            return trends
            
        except Exception as e:
            logger.error(f"Ошибка анализа трендов тональности: {e}")
            return {}
    
    def _analyze_emotion_trends(self, time_windows: List[Dict]) -> Dict:
        """Анализ трендов эмоций"""
        try:
            emotion_trends = {}
            
            for window in time_windows:
                window_emotions = {}
                text_count = 0
                
                for msg in window['messages']:
                    if msg['type'] == 'text':
                        text_count += 1
                        analysis = msg['analysis']
                        emotions = analysis.get('emotions', {})
                        
                        for emotion, score in emotions.items():
                            window_emotions[emotion] = window_emotions.get(emotion, 0) + score
                
                # Нормализуем по количеству текстовых сообщений
                if text_count > 0:
                    for emotion in window_emotions:
                        window_emotions[emotion] /= text_count
                        
                        if emotion not in emotion_trends:
                            emotion_trends[emotion] = []
                        emotion_trends[emotion].append(window_emotions[emotion])
            
            return emotion_trends
            
        except Exception as e:
            logger.error(f"Ошибка анализа трендов эмоций: {e}")
            return {}
    
    def _analyze_activity_patterns(self, time_windows: List[Dict]) -> Dict:
        """Анализ паттернов активности"""
        try:
            patterns = {
                'message_counts': [w['count'] for w in time_windows],
                'text_voice_ratio': [],
                'peak_activity_time': None,
                'avg_messages_per_window': 0
            }
            
            # Соотношение текст/голос
            for window in time_windows:
                text_count = len([m for m in window['messages'] if m['type'] == 'text'])
                voice_count = len([m for m in window['messages'] if m['type'] == 'voice'])
                
                if voice_count > 0:
                    ratio = text_count / voice_count
                else:
                    ratio = text_count if text_count > 0 else 0
                
                patterns['text_voice_ratio'].append(ratio)
            
            # Пиковая активность
            if patterns['message_counts']:
                max_count = max(patterns['message_counts'])
                max_index = patterns['message_counts'].index(max_count)
                if max_index < len(time_windows):
                    patterns['peak_activity_time'] = time_windows[max_index]['start_time']
                
                patterns['avg_messages_per_window'] = sum(patterns['message_counts']) / len(patterns['message_counts'])
            
            return patterns
            
        except Exception as e:
            logger.error(f"Ошибка анализа паттернов активности: {e}")
            return {}
    
    def _generate_temporal_insights(self, dynamics: Dict) -> List[str]:
        """Генерация инсайтов по временной динамике"""
        try:
            insights = []
            
            # Анализ трендов тональности
            sentiment_trends = dynamics.get('sentiment_trends', {})
            overall_trend = sentiment_trends.get('overall_trend', 'stable')
            
            if overall_trend == 'improving':
                insights.append("Тональность сообщений улучшается со временем")
            elif overall_trend == 'declining':
                insights.append("Наблюдается снижение позитивности сообщений")
            else:
                insights.append("Тональность остается стабильной")
            
            # Анализ активности
            activity_patterns = dynamics.get('activity_patterns', {})
            avg_messages = activity_patterns.get('avg_messages_per_window', 0)
            
            if avg_messages > 10:
                insights.append(f"Высокая активность: {avg_messages:.1f} сообщений в среднем за период")
            elif avg_messages > 5:
                insights.append(f"Умеренная активность: {avg_messages:.1f} сообщений за период")
            else:
                insights.append(f"Низкая активность: {avg_messages:.1f} сообщений за период")
            
            # Анализ соотношения модальностей
            text_voice_ratios = activity_patterns.get('text_voice_ratio', [])
            if text_voice_ratios:
                avg_ratio = sum(text_voice_ratios) / len(text_voice_ratios)
                if avg_ratio > 10:
                    insights.append("Преимущественно текстовое общение")
                elif avg_ratio > 1:
                    insights.append("Смешанное текстово-голосовое общение")
                else:
                    insights.append("Преимущественно голосовое общение")
            
            return insights
            
        except Exception as e:
            logger.error(f"Ошибка генерации инсайтов: {e}")
            return ["Ошибка анализа временной динамики"]
"""
Анализатор диалогов и голосовых сообщений
Фокус на саммари диалогов и анализе голосовых
"""

import logging
import asyncio
import os
import json
import tempfile
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

# Импортируем сервисы
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.openrouter_service import OpenRouterService
from analyzers.local_voice_analyzer import LocalVoiceAnalyzer
from prompts import AnalysisPrompts, SystemPrompts

logger = logging.getLogger(__name__)


class DialogSummaryAnalyzer:
    """Анализатор для саммари диалогов и голосовых сообщений"""
    
    def __init__(self):
        self.openrouter = OpenRouterService()
        self.voice_analyzer = LocalVoiceAnalyzer()
        self.initialized = False
    
    async def initialize(self):
        """Инициализация анализатора"""
        try:
            logger.info("🚀 Инициализация анализатора диалогов...")
            
            # Тест соединения с OpenRouter
            connection_test = await self.openrouter.test_connection()
            if not connection_test.get('success'):
                logger.error(f"❌ Ошибка подключения к OpenRouter: {connection_test.get('error')}")
                return False
            
            logger.info(f"✅ OpenRouter подключен (модель: {connection_test.get('model_tested')})")
            
            self.initialized = True
            logger.info("✅ Анализатор диалогов готов")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def analyze_dialog_summary(self, messages: List[Dict], 
                                   participant_names: List[str] = None) -> Dict:
        """Создание саммари диалога"""
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"📝 Создание саммари диалога из {len(messages)} сообщений")
            
            # Фильтруем только текстовые сообщения для саммари
            text_messages = [msg for msg in messages if msg.get('text')]
            
            if not text_messages:
                return {'success': False, 'error': 'No text messages for summary'}
            
            # Создаем контекст диалога
            dialog_context = self._prepare_dialog_context(text_messages, participant_names)
            
            # Создаем промпт для саммари
            summary_prompt = self._create_summary_prompt(dialog_context)
            
            # Получаем саммари через OpenRouter
            result = await self.openrouter.analyze_text(summary_prompt, task_type='analysis')
            
            if result.get('success'):
                summary_data = result.get('analysis', {})
                
                return {
                    'success': True,
                    'dialog_summary': {
                        'total_messages': len(text_messages),
                        'participants': participant_names or ['Участник 1', 'Участник 2'],
                        'time_span': self._get_time_span(text_messages),
                        'summary': summary_data,
                        'model_used': result.get('model_used'),
                        'created_at': datetime.now().isoformat()
                    }
                }
            else:
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания саммари: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_voice_messages(self, voice_messages: List[Dict]) -> Dict:
        """Анализ голосовых сообщений"""
        try:
            if not voice_messages:
                return {'success': False, 'error': 'No voice messages provided'}
            
            logger.info(f"🎤 Анализ {len(voice_messages)} голосовых сообщений")
            
            voice_analyses = []
            total_duration = 0
            
            for i, voice_msg in enumerate(voice_messages, 1):
                logger.info(f"🔄 Анализ голосового сообщения {i}/{len(voice_messages)}")
                
                try:
                    # Анализируем голосовое сообщение
                    voice_result = await self._analyze_single_voice(voice_msg)
                    
                    if voice_result.get('success'):
                        voice_analyses.append({
                            'message_id': voice_msg.get('id'),
                            'date': voice_msg.get('date'),
                            'duration': voice_msg.get('duration', 0),
                            'analysis': voice_result
                        })
                        total_duration += voice_msg.get('duration', 0)
                    
                except Exception as e:
                    logger.error(f"Ошибка анализа голосового сообщения {i}: {e}")
                    continue
            
            # Создаем общую сводку по голосовым
            voice_summary = self._create_voice_summary(voice_analyses, total_duration)
            
            return {
                'success': True,
                'voice_analysis': {
                    'total_messages': len(voice_messages),
                    'analyzed_messages': len(voice_analyses),
                    'total_duration': total_duration,
                    'analyses': voice_analyses,
                    'summary': voice_summary,
                    'created_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа голосовых: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _analyze_single_voice(self, voice_message: Dict) -> Dict:
        """Анализ одного голосового сообщения"""
        try:
            voice_file = voice_message.get('voice_file')
            duration = voice_message.get('duration', 10)
            
            if not voice_file:
                return {'success': False, 'error': 'No voice file provided'}
            
            # Используем локальный анализатор голоса
            result = await self.voice_analyzer.analyze(voice_file, duration)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка анализа голоса: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_dialog_context(self, messages: List[Dict], 
                               participant_names: List[str] = None) -> str:
        """Подготовка контекста диалога для анализа"""
        try:
            context_lines = []
            
            # Группируем сообщения по участникам
            participants = {}
            for msg in messages:
                from_id = msg.get('from_id', 'unknown')
                if from_id not in participants:
                    participants[from_id] = []
                participants[from_id].append(msg)
            
            # Создаем читаемый контекст
            participant_labels = {}
            if participant_names and len(participant_names) >= len(participants):
                for i, participant_id in enumerate(participants.keys()):
                    participant_labels[participant_id] = participant_names[i]
            else:
                for i, participant_id in enumerate(participants.keys()):
                    participant_labels[participant_id] = f"Участник {i+1}"
            
            # Сортируем сообщения по времени
            sorted_messages = sorted(messages, key=lambda x: x.get('date', ''))
            
            # Берем репрезентативную выборку (не более 50 сообщений)
            if len(sorted_messages) > 50:
                # Берем начало, середину и конец диалога
                sample_messages = (
                    sorted_messages[:15] +  # Начало
                    sorted_messages[len(sorted_messages)//2-10:len(sorted_messages)//2+10] +  # Середина
                    sorted_messages[-15:]  # Конец
                )
            else:
                sample_messages = sorted_messages
            
            # Формируем контекст
            for msg in sample_messages:
                from_id = msg.get('from_id', 'unknown')
                participant = participant_labels.get(from_id, 'Неизвестный')
                text = msg.get('text', '')[:200]  # Ограничиваем длину
                
                context_lines.append(f"{participant}: {text}")
            
            return '\n'.join(context_lines)
            
        except Exception as e:
            logger.error(f"Ошибка подготовки контекста: {e}")
            return "Ошибка подготовки контекста диалога"
    
    def _create_summary_prompt(self, dialog_context: str) -> str:
        """Создание промпта для саммари диалога"""
        return f"""Проанализируй следующий диалог и создай краткое саммари:

{dialog_context}

Создай структурированное саммари в JSON формате:
{{
  "main_topics": ["основная тема 1", "основная тема 2", "основная тема 3"],
  "key_points": ["ключевой момент 1", "ключевой момент 2", "ключевой момент 3"],
  "overall_tone": "общая тональность диалога (дружелюбная/деловая/напряженная/нейтральная)",
  "participant_roles": {{
    "Участник 1": "роль или характеристика первого участника",
    "Участник 2": "роль или характеристика второго участника"
  }},
  "dialog_outcome": "итог или результат диалога",
  "important_decisions": ["важное решение 1", "важное решение 2"],
  "emotional_dynamics": "эмоциональная динамика диалога",
  "summary_text": "краткое текстовое саммари диалога (2-3 предложения)"
}}

Отвечай только в JSON формате, без дополнительного текста."""
    
    def _get_time_span(self, messages: List[Dict]) -> Dict:
        """Получение временного промежутка диалога"""
        try:
            if not messages:
                return {}
            
            dates = [msg.get('date') for msg in messages if msg.get('date')]
            if not dates:
                return {}
            
            dates.sort()
            start_date = dates[0]
            end_date = dates[-1]
            
            # Парсим даты
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                duration = end_dt - start_dt
                
                return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_hours': duration.total_seconds() / 3600,
                    'duration_days': duration.days
                }
            except:
                return {
                    'start_date': start_date,
                    'end_date': end_date
                }
                
        except Exception as e:
            logger.error(f"Ошибка расчета временного промежутка: {e}")
            return {}
    
    def _create_voice_summary(self, voice_analyses: List[Dict], total_duration: int) -> Dict:
        """Создание сводки по голосовым сообщениям"""
        try:
            if not voice_analyses:
                return {'error': 'No voice analyses available'}
            
            # Анализируем паттерны в голосовых сообщениях
            durations = [analysis.get('duration', 0) for analysis in voice_analyses]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Собираем эмоциональные характеристики
            emotions_found = []
            speech_patterns = []
            
            for analysis in voice_analyses:
                voice_result = analysis.get('analysis', {})
                if voice_result.get('success'):
                    # Извлекаем найденные эмоции и паттерны
                    if 'emotions' in voice_result:
                        emotions_found.extend(voice_result['emotions'])
                    if 'speech_patterns' in voice_result:
                        speech_patterns.extend(voice_result['speech_patterns'])
            
            return {
                'total_duration_minutes': total_duration / 60,
                'average_message_duration': avg_duration,
                'message_count': len(voice_analyses),
                'dominant_emotions': list(set(emotions_found))[:5],  # Топ 5 уникальных
                'speech_characteristics': list(set(speech_patterns))[:5],
                'voice_activity_level': 'высокая' if len(voice_analyses) > 10 else 'умеренная' if len(voice_analyses) > 5 else 'низкая'
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания сводки голосовых: {e}")
            return {'error': str(e)}
    
    async def create_combined_analysis(self, messages: List[Dict], 
                                     participant_names: List[str] = None) -> Dict:
        """Комбинированный анализ: саммари диалога + голосовые сообщения"""
        try:
            logger.info("🔮 Создание комбинированного анализа диалога")
            
            # Разделяем сообщения на текстовые и голосовые
            text_messages = [msg for msg in messages if msg.get('text')]
            voice_messages = [msg for msg in messages if msg.get('type') == 'voice']
            
            results = {
                'success': True,
                'analysis_type': 'combined_dialog_analysis',
                'created_at': datetime.now().isoformat(),
                'statistics': {
                    'total_messages': len(messages),
                    'text_messages': len(text_messages),
                    'voice_messages': len(voice_messages)
                }
            }
            
            # Анализ текстового диалога (саммари)
            if text_messages:
                logger.info("📝 Создание саммари текстового диалога...")
                dialog_result = await self.analyze_dialog_summary(text_messages, participant_names)
                
                if dialog_result.get('success'):
                    results['dialog_summary'] = dialog_result['dialog_summary']
                else:
                    results['dialog_summary_error'] = dialog_result.get('error')
            
            # Анализ голосовых сообщений
            if voice_messages:
                logger.info("🎤 Анализ голосовых сообщений...")
                voice_result = await self.analyze_voice_messages(voice_messages)
                
                if voice_result.get('success'):
                    results['voice_analysis'] = voice_result['voice_analysis']
                else:
                    results['voice_analysis_error'] = voice_result.get('error')
            
            # Создаем общие инсайты
            results['insights'] = self._generate_combined_insights(results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка комбинированного анализа: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_combined_insights(self, analysis_results: Dict) -> List[str]:
        """Генерация общих инсайтов по комбинированному анализу"""
        try:
            insights = []
            
            stats = analysis_results.get('statistics', {})
            total_messages = stats.get('total_messages', 0)
            text_count = stats.get('text_messages', 0)
            voice_count = stats.get('voice_messages', 0)
            
            # Общая статистика
            insights.append(f"Проанализирован диалог из {total_messages} сообщений")
            
            if text_count > 0 and voice_count > 0:
                ratio = text_count / voice_count
                if ratio > 3:
                    insights.append("Преимущественно текстовое общение")
                elif ratio < 0.5:
                    insights.append("Преимущественно голосовое общение")
                else:
                    insights.append("Смешанный формат общения (текст + голос)")
            
            # Инсайты из саммари диалога
            dialog_summary = analysis_results.get('dialog_summary', {})
            if dialog_summary:
                summary_data = dialog_summary.get('summary', {})
                if isinstance(summary_data, dict):
                    overall_tone = summary_data.get('overall_tone')
                    if overall_tone:
                        insights.append(f"Общая тональность диалога: {overall_tone}")
                    
                    main_topics = summary_data.get('main_topics', [])
                    if main_topics:
                        insights.append(f"Основные темы: {', '.join(main_topics[:3])}")
            
            # Инсайты из голосового анализа
            voice_analysis = analysis_results.get('voice_analysis', {})
            if voice_analysis:
                voice_summary = voice_analysis.get('summary', {})
                activity_level = voice_summary.get('voice_activity_level')
                if activity_level:
                    insights.append(f"Голосовая активность: {activity_level}")
                
                total_duration = voice_summary.get('total_duration_minutes', 0)
                if total_duration > 0:
                    insights.append(f"Общая длительность голосовых: {total_duration:.1f} минут")
            
            return insights[:5]  # Максимум 5 инсайтов
            
        except Exception as e:
            logger.error(f"Ошибка генерации инсайтов: {e}")
            return ["Ошибка генерации инсайтов"]
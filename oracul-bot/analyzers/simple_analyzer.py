"""
Упрощенный анализатор диалогов без зависимостей от torch
"""

import logging
import asyncio
import os
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SimpleAnalyzer:
    """Упрощенный анализатор для базового функционала"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Инициализация анализатора"""
        try:
            logger.info("🚀 Инициализация упрощенного анализатора...")
            self.initialized = True
            logger.info("✅ Упрощенный анализатор готов")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def create_combined_analysis(self, messages: List[Dict], participant_names: List[str] = None) -> Dict:
        """Создание базового анализа сообщений"""
        try:
            if not messages:
                return {
                    'success': False,
                    'error': 'Нет сообщений для анализа'
                }
            
            # Базовая статистика
            total_messages = len(messages)
            text_messages = len([msg for msg in messages if msg.get('type') == 'text'])
            voice_messages = len([msg for msg in messages if msg.get('type') == 'voice'])
            
            # Анализ текстов
            all_text = ' '.join([msg.get('text', '') for msg in messages if msg.get('text')])
            word_count = len(all_text.split()) if all_text else 0
            
            # Основные темы (простой анализ по ключевым словам)
            main_topics = self._extract_simple_topics(all_text)
            
            # Тональность (базовая)
            overall_tone = self._analyze_simple_tone(all_text)
            
            # Создаем результат
            result = {
                'success': True,
                'statistics': {
                    'total_messages': total_messages,
                    'text_messages': text_messages,
                    'voice_messages': voice_messages,
                    'word_count': word_count
                },
                'dialog_summary': {
                    'summary': {
                        'main_topics': main_topics,
                        'overall_tone': overall_tone,
                        'summary_text': f'Проанализировано {total_messages} сообщений. Основные темы: {", ".join(main_topics[:3])}. Общая тональность: {overall_tone}.'
                    }
                },
                'insights': [
                    f'Всего сообщений: {total_messages}',
                    f'Текстовых сообщений: {text_messages}',
                    f'Голосовых сообщений: {voice_messages}',
                    f'Общее количество слов: {word_count}',
                    f'Основная тональность: {overall_tone}'
                ],
                'chat_type': 'personal' if total_messages > 0 else 'unknown'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка анализа: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_simple_topics(self, text: str) -> List[str]:
        """Простое извлечение тем по ключевым словам"""
        if not text:
            return ['общение']
        
        text_lower = text.lower()
        
        # Простые категории тем
        topic_keywords = {
            'работа': ['работа', 'работать', 'офис', 'проект', 'задача', 'встреча', 'коллега'],
            'семья': ['семья', 'родители', 'мама', 'папа', 'дети', 'ребенок', 'дом'],
            'друзья': ['друг', 'подруга', 'встреча', 'гулять', 'вместе'],
            'учеба': ['учеба', 'университет', 'экзамен', 'лекция', 'студент'],
            'здоровье': ['здоровье', 'врач', 'болеть', 'лечение', 'больница'],
            'развлечения': ['фильм', 'игра', 'музыка', 'концерт', 'кино'],
            'путешествия': ['поездка', 'отпуск', 'путешествие', 'самолет', 'отель'],
            'еда': ['еда', 'ресторан', 'готовить', 'обед', 'ужин'],
            'спорт': ['спорт', 'тренировка', 'футбол', 'бег', 'зал'],
            'технологии': ['компьютер', 'интернет', 'программа', 'сайт', 'приложение']
        }
        
        found_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics if found_topics else ['общение', 'повседневность']
    
    def _analyze_simple_tone(self, text: str) -> str:
        """Простой анализ тональности"""
        if not text:
            return 'нейтральная'
        
        text_lower = text.lower()
        
        positive_words = ['хорошо', 'отлично', 'супер', 'классно', 'круто', 'спасибо', 'люблю', 'рад', 'счастлив']
        negative_words = ['плохо', 'ужасно', 'грустно', 'злой', 'расстроен', 'проблема', 'беда', 'болит']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'позитивная'
        elif negative_count > positive_count:
            return 'негативная'
        else:
            return 'нейтральная'
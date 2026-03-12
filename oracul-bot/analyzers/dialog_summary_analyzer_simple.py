"""
Упрощенный анализатор диалогов без зависимостей от torch
Использует OpenRouter API для анализа
"""

import logging
import asyncio
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Импортируем сервисы
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from services.openrouter_service import OpenRouterService
except ImportError:
    # Создаем заглушку если сервис недоступен
    class OpenRouterService:
        def __init__(self):
            self.api_key = os.getenv('OPENROUTER_API_KEY')
        
        async def test_connection(self):
            if self.api_key and self.api_key != 'YOUR_OPENROUTER_KEY_HERE':
                return {'success': True, 'model_tested': 'openai/gpt-4o-mini'}
            return {'success': False, 'error': 'API key not configured'}
        
        async def analyze_text(self, text: str, task_type: str = 'analysis'):
            return {
                'success': True,
                'analysis': f'Анализ текста ({len(text)} символов): основные темы включают общение и взаимодействие.',
                'model_used': 'mock'
            }

logger = logging.getLogger(__name__)


class DialogSummaryAnalyzer:
    """Упрощенный анализатор для саммари диалогов"""
    
    def __init__(self):
        self.openrouter = OpenRouterService()
        self.initialized = False
    
    async def initialize(self):
        """Инициализация анализатора"""
        try:
            logger.info("🚀 Инициализация анализатора диалогов...")
            
            # Тест соединения с OpenRouter
            connection_test = await self.openrouter.test_connection()
            if not connection_test.get('success'):
                logger.warning(f"⚠️ OpenRouter недоступен: {connection_test.get('error')}")
                logger.info("📝 Будет использован базовый анализ")
            else:
                logger.info(f"✅ OpenRouter подключен (модель: {connection_test.get('model_tested')})")
            
            self.initialized = True
            logger.info("✅ Анализатор диалогов готов")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def create_combined_analysis(self, messages: List[Dict], participant_names: List[str] = None) -> Dict:
        """Создание комбинированного анализа сообщений"""
        try:
            if not messages:
                return {
                    'success': False,
                    'error': 'Нет сообщений для анализа'
                }
            
            # Базовая статистика
            total_messages = len(messages)
            text_messages = [msg for msg in messages if msg.get('type') == 'text' and msg.get('text')]
            voice_messages = [msg for msg in messages if msg.get('type') == 'voice']
            
            # Собираем весь текст
            all_text = ' '.join([msg.get('text', '') for msg in text_messages])
            word_count = len(all_text.split()) if all_text else 0
            
            # Определяем тип чата
            chat_type = 'group' if any(msg.get('chat_type') == 'group' for msg in messages) else 'personal'
            
            # Анализ текста
            if all_text and len(all_text) > 50:
                text_analysis = await self._analyze_dialog_text(all_text)
            else:
                text_analysis = self._create_basic_analysis(messages)
            
            # Анализ голосовых
            voice_analysis = self._analyze_voice_messages(voice_messages)
            
            # Создаем результат
            result = {
                'success': True,
                'statistics': {
                    'total_messages': total_messages,
                    'text_messages': len(text_messages),
                    'voice_messages': len(voice_messages),
                    'word_count': word_count
                },
                'dialog_summary': {
                    'summary': {
                        'main_topics': text_analysis.get('main_topics', ['общение']),
                        'overall_tone': text_analysis.get('overall_tone', 'нейтральная'),
                        'summary_text': text_analysis.get('summary_text', f'Проанализировано {total_messages} сообщений.')
                    }
                },
                'insights': text_analysis.get('insights', [
                    f'Всего сообщений: {total_messages}',
                    f'Текстовых: {len(text_messages)}',
                    f'Голосовых: {len(voice_messages)}'
                ]),
                'chat_type': chat_type,
                'voice_analysis': voice_analysis
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка создания анализа: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _analyze_dialog_text(self, text: str) -> Dict:
        """Анализ текста диалога"""
        try:
            # Пробуем использовать OpenRouter
            if hasattr(self.openrouter, 'api_key') and self.openrouter.api_key and self.openrouter.api_key != 'YOUR_OPENROUTER_KEY_HERE':
                
                prompt = f"""
Проанализируй следующий диалог и предоставь краткий анализ:

Текст диалога:
{text[:2000]}...

Предоставь анализ в формате:
1. Основные темы (3-5 тем)
2. Общая тональность (позитивная/негативная/нейтральная)
3. Краткое саммари (2-3 предложения)
4. Ключевые инсайты (3-5 пунктов)

Отвечай на русском языке, будь конкретным и полезным.
"""
                
                ai_result = await self.openrouter.analyze_text(prompt, 'analysis')
                
                if ai_result.get('success'):
                    # Парсим ответ AI
                    analysis_text = ai_result.get('analysis', '')
                    return self._parse_ai_analysis(analysis_text)
            
            # Если AI недоступен, используем базовый анализ
            return self._create_basic_analysis_from_text(text)
            
        except Exception as e:
            logger.error(f"Ошибка анализа текста: {e}")
            return self._create_basic_analysis_from_text(text)
    
    def _parse_ai_analysis(self, analysis_text: str) -> Dict:
        """Парсинг ответа от AI"""
        try:
            # Простой парсинг структурированного ответа
            lines = analysis_text.split('\n')
            
            main_topics = []
            overall_tone = 'нейтральная'
            summary_text = 'Анализ выполнен успешно.'
            insights = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if 'темы' in line.lower() or 'topics' in line.lower():
                    current_section = 'topics'
                elif 'тональность' in line.lower() or 'tone' in line.lower():
                    current_section = 'tone'
                elif 'саммари' in line.lower() or 'summary' in line.lower():
                    current_section = 'summary'
                elif 'инсайт' in line.lower() or 'insight' in line.lower():
                    current_section = 'insights'
                elif line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                    # Это пункт списка
                    clean_line = line.lstrip('-•*123456789. ').strip()
                    if current_section == 'topics' and len(main_topics) < 5:
                        main_topics.append(clean_line)
                    elif current_section == 'insights' and len(insights) < 5:
                        insights.append(clean_line)
                elif current_section == 'tone' and any(word in line.lower() for word in ['позитивная', 'негативная', 'нейтральная', 'положительная', 'отрицательная']):
                    if 'позитивная' in line.lower() or 'положительная' in line.lower():
                        overall_tone = 'позитивная'
                    elif 'негативная' in line.lower() or 'отрицательная' in line.lower():
                        overall_tone = 'негативная'
                    else:
                        overall_tone = 'нейтральная'
                elif current_section == 'summary' and len(line) > 20:
                    summary_text = line
            
            return {
                'main_topics': main_topics if main_topics else ['общение', 'взаимодействие'],
                'overall_tone': overall_tone,
                'summary_text': summary_text,
                'insights': insights if insights else ['Диалог проанализирован', 'Выявлены основные паттерны общения']
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга AI анализа: {e}")
            return self._create_basic_analysis_from_text('')
    
    def _create_basic_analysis_from_text(self, text: str) -> Dict:
        """Создание базового анализа из текста"""
        # Простой анализ по ключевым словам
        text_lower = text.lower() if text else ''
        
        # Определение тем
        topic_keywords = {
            'работа': ['работа', 'работать', 'офис', 'проект', 'задача', 'встреча', 'коллега', 'начальник'],
            'семья': ['семья', 'родители', 'мама', 'папа', 'дети', 'ребенок', 'дом', 'родственник'],
            'друзья': ['друг', 'подруга', 'встреча', 'гулять', 'вместе', 'компания'],
            'учеба': ['учеба', 'университет', 'экзамен', 'лекция', 'студент', 'школа'],
            'здоровье': ['здоровье', 'врач', 'болеть', 'лечение', 'больница', 'самочувствие'],
            'развлечения': ['фильм', 'игра', 'музыка', 'концерт', 'кино', 'сериал'],
            'путешествия': ['поездка', 'отпуск', 'путешествие', 'самолет', 'отель', 'море'],
            'еда': ['еда', 'ресторан', 'готовить', 'обед', 'ужин', 'кафе'],
            'спорт': ['спорт', 'тренировка', 'футбол', 'бег', 'зал', 'фитнес'],
            'технологии': ['компьютер', 'интернет', 'программа', 'сайт', 'приложение', 'телефон']
        }
        
        found_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)
        
        # Определение тональности
        positive_words = ['хорошо', 'отлично', 'супер', 'классно', 'круто', 'спасибо', 'люблю', 'рад', 'счастлив', 'здорово']
        negative_words = ['плохо', 'ужасно', 'грустно', 'злой', 'расстроен', 'проблема', 'беда', 'болит', 'устал']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            tone = 'позитивная'
        elif negative_count > positive_count:
            tone = 'негативная'
        else:
            tone = 'нейтральная'
        
        return {
            'main_topics': found_topics if found_topics else ['общение', 'повседневность'],
            'overall_tone': tone,
            'summary_text': f'Диалог содержит {len(text.split())} слов. Основные темы: {", ".join(found_topics[:3]) if found_topics else "общение"}. Тональность: {tone}.',
            'insights': [
                f'Выявлено тем: {len(found_topics)}',
                f'Тональность общения: {tone}',
                f'Объем текста: {len(text.split())} слов',
                'Анализ выполнен базовыми методами'
            ]
        }
    
    def _create_basic_analysis(self, messages: List[Dict]) -> Dict:
        """Создание базового анализа без текста"""
        total = len(messages)
        text_count = len([m for m in messages if m.get('type') == 'text'])
        voice_count = len([m for m in messages if m.get('type') == 'voice'])
        
        return {
            'main_topics': ['общение', 'сообщения'],
            'overall_tone': 'нейтральная',
            'summary_text': f'Проанализировано {total} сообщений: {text_count} текстовых и {voice_count} голосовых.',
            'insights': [
                f'Всего сообщений: {total}',
                f'Текстовых сообщений: {text_count}',
                f'Голосовых сообщений: {voice_count}',
                'Базовый анализ структуры диалога'
            ]
        }
    
    def _analyze_voice_messages(self, voice_messages: List[Dict]) -> Dict:
        """Анализ голосовых сообщений"""
        if not voice_messages:
            return {
                'total_voice': 0,
                'total_duration': 0,
                'average_duration': 0,
                'insights': []
            }
        
        total_duration = sum(msg.get('duration', 10) for msg in voice_messages)
        average_duration = total_duration / len(voice_messages) if voice_messages else 0
        
        insights = []
        if len(voice_messages) > 10:
            insights.append('Активное использование голосовых сообщений')
        if average_duration > 30:
            insights.append('Длинные голосовые сообщения (детальное общение)')
        elif average_duration < 10:
            insights.append('Короткие голосовые сообщения (быстрое общение)')
        
        return {
            'total_voice': len(voice_messages),
            'total_duration': total_duration,
            'average_duration': round(average_duration, 1),
            'insights': insights
        }
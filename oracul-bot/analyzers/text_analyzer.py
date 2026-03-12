"""
Анализатор текста для Oracul Bot
"""

import logging
import asyncio
from typing import Dict, List, Optional
import openai
from textblob import TextBlob
import re

from config.settings import settings

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """Анализатор текстовых сообщений"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def analyze(self, text: str, user_context: Optional[Dict] = None) -> Dict:
        """
        Комплексный анализ текста
        
        Args:
            text: Текст для анализа
            user_context: Контекст пользователя (история, предпочтения)
            
        Returns:
            Dict с результатами анализа
        """
        try:
            # Предварительная обработка
            cleaned_text = self._preprocess_text(text)
            
            if len(cleaned_text) < 10:
                return {
                    'success': False,
                    'error': 'Текст слишком короткий для анализа'
                }
            
            # Параллельный анализ разных аспектов
            tasks = [
                self._analyze_sentiment(cleaned_text),
                self._analyze_emotions(cleaned_text),
                self._analyze_personality(cleaned_text),
                self._analyze_with_llm(cleaned_text, user_context)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Объединяем результаты
            analysis = {
                'success': True,
                'text_length': len(text),
                'processed_text_length': len(cleaned_text),
                'sentiment': results[0] if not isinstance(results[0], Exception) else None,
                'emotions': results[1] if not isinstance(results[1], Exception) else None,
                'personality': results[2] if not isinstance(results[2], Exception) else None,
                'llm_analysis': results[3] if not isinstance(results[3], Exception) else None,
                'recommendations': []
            }
            
            # Генерируем рекомендации
            analysis['recommendations'] = await self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Предварительная обработка текста"""
        # Удаляем лишние пробелы и переносы
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Удаляем URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Удаляем упоминания и хештеги (но оставляем эмоциональную окраску)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        return text.strip()
    
    async def _analyze_sentiment(self, text: str) -> Dict:
        """Анализ тональности с помощью TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Определяем тональность
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'label': label,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'label': 'neutral', 'confidence': 0.0}
    
    async def _analyze_emotions(self, text: str) -> Dict:
        """Анализ эмоций (упрощенная версия)"""
        try:
            # Словари эмоциональных слов (упрощенная версия)
            emotion_keywords = {
                'joy': ['радость', 'счастье', 'веселье', 'восторг', 'удовольствие', 'смех', '😊', '😄', '😃', '🎉'],
                'sadness': ['грусть', 'печаль', 'тоска', 'уныние', 'слезы', '😢', '😭', '😔'],
                'anger': ['злость', 'гнев', 'ярость', 'бешенство', 'раздражение', '😠', '😡', '🤬'],
                'fear': ['страх', 'боязнь', 'ужас', 'тревога', 'паника', '😨', '😰', '😱'],
                'surprise': ['удивление', 'изумление', 'шок', 'неожиданность', '😲', '😮', '🤯'],
                'love': ['любовь', 'обожание', 'привязанность', 'нежность', '❤️', '💕', '😍']
            }
            
            text_lower = text.lower()
            emotions = {}
            
            for emotion, keywords in emotion_keywords.items():
                score = 0
                for keyword in keywords:
                    score += text_lower.count(keyword.lower())
                
                # Нормализуем по длине текста
                emotions[emotion] = min(score / max(len(text.split()), 1), 1.0)
            
            return emotions
            
        except Exception as e:
            logger.error(f"Emotion analysis error: {e}")
            return {}
    
    async def _analyze_personality(self, text: str) -> Dict:
        """Анализ личностных черт (Big Five упрощенно)"""
        try:
            # Упрощенные индикаторы личностных черт
            personality_indicators = {
                'openness': ['творчество', 'искусство', 'новое', 'идея', 'фантазия', 'воображение'],
                'conscientiousness': ['план', 'порядок', 'организация', 'дисциплина', 'ответственность'],
                'extraversion': ['люди', 'общение', 'вечеринка', 'друзья', 'социальный'],
                'agreeableness': ['помощь', 'доброта', 'сочувствие', 'понимание', 'поддержка'],
                'neuroticism': ['стресс', 'тревога', 'беспокойство', 'нервы', 'волнение']
            }
            
            text_lower = text.lower()
            personality = {}
            
            for trait, indicators in personality_indicators.items():
                score = 0
                for indicator in indicators:
                    score += text_lower.count(indicator)
                
                # Нормализуем
                personality[trait] = min(score / max(len(text.split()), 1) * 10, 1.0)
            
            return personality
            
        except Exception as e:
            logger.error(f"Personality analysis error: {e}")
            return {}
    
    async def _analyze_with_llm(self, text: str, user_context: Optional[Dict] = None) -> Dict:
        """Глубокий анализ с помощью LLM"""
        try:
            context_info = ""
            if user_context:
                context_info = f"Контекст пользователя: {user_context.get('summary', '')}\n"
            
            prompt = f"""
Проанализируй следующий текст и дай психологическую оценку автора:

{context_info}
Текст: "{text}"

Проанализируй:
1. Эмоциональное состояние автора
2. Основные личностные черты
3. Стиль мышления и коммуникации
4. Возможные потребности и мотивации
5. Уровень стресса или благополучия

Ответь в формате JSON:
{{
    "emotional_state": "описание эмоционального состояния",
    "personality_traits": ["черта1", "черта2", "черта3"],
    "thinking_style": "описание стиля мышления",
    "needs_motivations": ["потребность1", "потребность2"],
    "stress_level": "низкий/средний/высокий",
    "key_insights": ["инсайт1", "инсайт2", "инсайт3"]
}}
            """
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты опытный психолог-аналитик. Анализируй тексты профессионально и деликатно."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Парсим JSON ответ
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return {}
    
    async def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация аналитических наблюдений"""
        observations = []
        
        try:
            sentiment = analysis.get('sentiment', {})
            emotions = analysis.get('emotions', {})
            llm_analysis = analysis.get('llm_analysis', {})
            
            # Наблюдения на основе тональности
            if sentiment.get('label') == 'negative' and sentiment.get('confidence', 0) > 0.7:
                observations.append("Выраженная негативная тональность в тексте")
            elif sentiment.get('label') == 'positive' and sentiment.get('confidence', 0) > 0.7:
                observations.append("Выраженная позитивная тональность в тексте")
            
            # Наблюдения на основе эмоций
            dominant_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
            if dominant_emotions and dominant_emotions[0][1] > 0.5:
                emotion_name = dominant_emotions[0][0]
                observations.append(f"Доминирующий эмоциональный маркер: {emotion_name}")
            
            # Наблюдения от LLM
            if llm_analysis.get('key_insights'):
                for insight in llm_analysis['key_insights'][:2]:
                    observations.append(f"Паттерн: {insight}")
            
            # Общие наблюдения
            if not observations:
                observations.append("Текст содержит смешанные эмоциональные маркеры")
            
            return observations[:4]  # Максимум 4 наблюдения
            
        except Exception as e:
            logger.error(f"Observations generation error: {e}")
            return ["Анализ завершен. Данные доступны для интерпретации."]
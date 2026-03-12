"""
Локальный анализатор текста для Oracul Bot
Использует локальные модели + современные OpenRouter API
"""

import logging
import asyncio
from typing import Dict, List, Optional
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, AutoModel
)
import numpy as np
from textblob import TextBlob
import re
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Импортируем современные анализаторы
try:
    from services.openrouter_service import OpenRouterService
    MODERN_MODELS_AVAILABLE = True
except ImportError:
    MODERN_MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


class LocalTextAnalyzer:
    """Анализатор текста с локальными моделями"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Инициализируем локальные модели
        self._init_models()
        
        # Инициализируем современные модели (OpenRouter)
        self.modern_service = None
        if MODERN_MODELS_AVAILABLE and os.getenv('OPENROUTER_API_KEY'):
            try:
                self.modern_service = OpenRouterService()
                logger.info("✅ Modern OpenRouter service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize modern service: {e}")
                self.modern_service = None
        else:
            logger.info("⚠️ Modern models not available (missing OpenRouter API key)")
    
    def _init_models(self):
        """Инициализация локальных моделей"""
        try:
            # Модель для анализа тональности (русская)
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="blanchefort/rubert-base-cased-sentiment",
                device=0 if self.device == "cuda" else -1
            )
            
            # Модель для эмоций (многоязычная)
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if self.device == "cuda" else -1
            )
            
            # Модель для генерации текста (русская)
            self.generation_model = pipeline(
                "text-generation",
                model="ai-forever/rugpt3small_based_on_gpt2",
                device=0 if self.device == "cuda" else -1,
                max_length=200,
                do_sample=True,
                temperature=0.7
            )
            
            # Модель для эмбеддингов
            self.embedding_model = AutoModel.from_pretrained(
                "DeepPavlov/rubert-base-cased-sentence"
            ).to(self.device)
            self.embedding_tokenizer = AutoTokenizer.from_pretrained(
                "DeepPavlov/rubert-base-cased-sentence"
            )
            
            logger.info("✅ Локальные модели инициализированы")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации моделей: {e}")
            # Fallback к базовым методам
            self.sentiment_model = None
            self.emotion_model = None
            self.generation_model = None
            self.embedding_model = None
    
    async def analyze(self, text: str, user_context: Optional[Dict] = None, use_modern: bool = True) -> Dict:
        """
        Комплексный анализ текста с локальными + современными моделями
        
        Args:
            text: Текст для анализа
            user_context: Контекст пользователя
            use_modern: Использовать современные OpenRouter модели
            
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
                self._analyze_sentiment_local(cleaned_text),
                self._analyze_emotions_local(cleaned_text),
                self._analyze_personality_local(cleaned_text),
                self._analyze_with_local_llm(cleaned_text, user_context)
            ]
            
            # Добавляем современный анализ если доступен
            if use_modern and self.modern_service:
                tasks.append(self._analyze_with_modern_models(cleaned_text))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Объединяем результаты
            analysis = {
                'success': True,
                'text_length': len(text),
                'processed_text_length': len(cleaned_text),
                'sentiment': results[0] if not isinstance(results[0], Exception) else None,
                'emotions': results[1] if not isinstance(results[1], Exception) else None,
                'personality': results[2] if not isinstance(results[2], Exception) else None,
                'local_llm_analysis': results[3] if not isinstance(results[3], Exception) else None,
                'recommendations': [],
                'analysis_methods': ['local_models']
            }
            
            # Добавляем современный анализ если был выполнен
            if use_modern and self.modern_service and len(results) > 4:
                modern_result = results[4]
                if not isinstance(modern_result, Exception) and modern_result.get('success'):
                    analysis['modern_analysis'] = modern_result
                    analysis['analysis_methods'].append('openrouter_api')
                    logger.info("✅ Modern analysis completed successfully")
            
            # Генерируем наблюдения
            analysis['recommendations'] = await self._generate_observations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive text analysis: {e}")
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
        
        # Удаляем упоминания и хештеги
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        return text.strip()
    
    async def _analyze_sentiment_local(self, text: str) -> Dict:
        """Анализ тональности с локальной моделью"""
        try:
            if self.sentiment_model:
                # Используем локальную модель
                result = self.sentiment_model(text[:512])  # Ограничиваем длину
                
                if result:
                    label = result[0]['label'].lower()
                    score = result[0]['score']
                    
                    # Маппинг меток
                    label_mapping = {
                        'positive': 'positive',
                        'negative': 'negative',
                        'neutral': 'neutral'
                    }
                    
                    return {
                        'label': label_mapping.get(label, 'neutral'),
                        'confidence': score,
                        'raw_result': result[0]
                    }
            
            # Fallback к TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'label': label,
                'confidence': abs(polarity),
                'polarity': polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
            
        except Exception as e:
            logger.error(f"Local sentiment analysis error: {e}")
            return {'label': 'neutral', 'confidence': 0.0}
    
    async def _analyze_emotions_local(self, text: str) -> Dict:
        """Анализ эмоций с локальной моделью"""
        try:
            if self.emotion_model:
                # Используем локальную модель эмоций
                result = self.emotion_model(text[:512])
                
                emotions = {}
                for item in result:
                    emotion = item['label'].lower()
                    score = item['score']
                    emotions[emotion] = score
                
                return emotions
            
            # Fallback к словарному методу
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
                
                emotions[emotion] = min(score / max(len(text.split()), 1), 1.0)
            
            return emotions
            
        except Exception as e:
            logger.error(f"Local emotion analysis error: {e}")
            return {}
    
    async def _analyze_personality_local(self, text: str) -> Dict:
        """Анализ личностных черт с локальными методами"""
        try:
            # Используем эмбеддинги для анализа личности
            if self.embedding_model and self.embedding_tokenizer:
                # Получаем эмбеддинги текста
                inputs = self.embedding_tokenizer(
                    text[:512], 
                    return_tensors="pt", 
                    truncation=True, 
                    padding=True
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.embedding_model(**inputs)
                    embeddings = outputs.last_hidden_state.mean(dim=1)
                
                # Простая эвристика на основе эмбеддингов
                embedding_vector = embeddings.cpu().numpy()[0]
                
                # Анализируем различные аспекты на основе паттернов в эмбеддингах
                personality = {
                    'openness': float(np.mean(embedding_vector[:100])),
                    'conscientiousness': float(np.mean(embedding_vector[100:200])),
                    'extraversion': float(np.mean(embedding_vector[200:300])),
                    'agreeableness': float(np.mean(embedding_vector[300:400])),
                    'neuroticism': float(np.mean(embedding_vector[400:500]))
                }
                
                # Нормализуем значения
                for trait in personality:
                    personality[trait] = max(0, min(1, (personality[trait] + 1) / 2))
                
                return personality
            
            # Fallback к словарному методу
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
                
                personality[trait] = min(score / max(len(text.split()), 1) * 10, 1.0)
            
            return personality
            
        except Exception as e:
            logger.error(f"Local personality analysis error: {e}")
            return {}
    
    async def _analyze_with_local_llm(self, text: str, user_context: Optional[Dict] = None) -> Dict:
        """Анализ с локальной LLM"""
        try:
            if not self.generation_model:
                return {}
            
            context_info = ""
            if user_context:
                context_info = f"Контекст: {user_context.get('summary', '')}\n"
            
            prompt = f"""
{context_info}Анализ текста: "{text[:200]}"

Основные наблюдения:
1. Эмоциональное состояние:"""
            
            # Генерируем анализ
            result = self.generation_model(
                prompt,
                max_length=len(prompt) + 100,
                num_return_sequences=1,
                temperature=0.3,
                do_sample=True
            )
            
            generated_text = result[0]['generated_text']
            analysis_part = generated_text[len(prompt):].strip()
            
            return {
                'generated_analysis': analysis_part,
                'prompt_used': prompt,
                'model_confidence': 0.7  # Примерная оценка
            }
            
        except Exception as e:
            logger.error(f"Local LLM analysis error: {e}")
            return {}
    
    async def _generate_observations(self, analysis: Dict) -> List[str]:
        """Генерация аналитических наблюдений"""
        observations = []
        
        try:
            sentiment = analysis.get('sentiment', {})
            emotions = analysis.get('emotions', {})
            personality = analysis.get('personality', {})
            
            # Наблюдения на основе тональности
            if sentiment.get('confidence', 0) > 0.7:
                tone = sentiment.get('label', 'neutral')
                observations.append(f"Выраженная {tone} тональность (уверенность: {sentiment['confidence']*100:.0f}%)")
            
            # Наблюдения на основе эмоций
            if emotions:
                dominant_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
                for emotion, score in dominant_emotions:
                    if score > 0.3:
                        observations.append(f"Эмоциональный маркер: {emotion} ({score*100:.0f}%)")
            
            # Наблюдения на основе личности
            if personality:
                high_traits = [(trait, score) for trait, score in personality.items() if score > 0.6]
                for trait, score in high_traits:
                    observations.append(f"Личностная тенденция: {trait} ({score*100:.0f}%)")
            
            # Общие наблюдения
            if not observations:
                observations.append("Текст содержит смешанные паттерны")
            
            return observations[:4]
            
        except Exception as e:
            logger.error(f"Observations generation error: {e}")
            return ["Анализ завершен. Данные доступны для интерпретации."]
    
    async def _analyze_with_modern_models(self, text: str) -> Dict:
        """Анализ с современными OpenRouter моделями"""
        try:
            if not self.modern_service:
                return {
                    'success': False,
                    'error': 'Modern service not available'
                }
            
            # Используем OpenRouter для анализа
            result = await self.modern_service.analyze_text(text, 'analysis')
            
            if result.get('success'):
                return {
                    'success': True,
                    'openrouter_analysis': result.get('analysis', {}),
                    'model_used': result.get('model_used'),
                    'raw_response': result.get('raw_response', '')[:200]  # Первые 200 символов
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown OpenRouter error')
                }
                
        except Exception as e:
            logger.error(f"Modern models analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
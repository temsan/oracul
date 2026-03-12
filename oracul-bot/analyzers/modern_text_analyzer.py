"""
Современный анализатор текста с лучшими моделями 2024
Использует новейшие модели с Hugging Face + OpenRouter API
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logger = logging.getLogger(__name__)


class ModernTextAnalyzer:
    """Современный анализатор с лучшими моделями 2024"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # OpenRouter API настройки
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        
        # Инициализируем модели
        self._init_modern_models()
    
    def _init_modern_models(self):
        """Инициализация современных моделей"""
        try:
            # 1. Современная модель эмоций (2023, 9 эмоций)
            logger.info("Loading modern emotion model...")
            self.emotion_model = pipeline(
                "text-classification",
                model="Djacon/rubert-tiny2-russian-emotion-detection",
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            # 2. Улучшенная модель тональности
            logger.info("Loading improved sentiment model...")
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="sismetanin/rubert-ru-sentiment-rusentiment",
                device=0 if self.device == "cuda" else -1
            )
            
            # 3. Многоязычная модель для сравнения
            logger.info("Loading multilingual model...")
            self.multilingual_model = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=0 if self.device == "cuda" else -1
            )
            
            # 4. Компактная модель для быстрого анализа
            logger.info("Loading compact model...")
            self.compact_model = pipeline(
                "sentiment-analysis",
                model="seara/rubert-tiny2-russian-sentiment",
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info("✅ Современные модели инициализированы")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации современных моделей: {e}")
            # Fallback к базовым моделям
            self._init_fallback_models()
    
    def _init_fallback_models(self):
        """Fallback модели если современные не загрузились"""
        try:
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="blanchefort/rubert-base-cased-sentiment",
                device=0 if self.device == "cuda" else -1
            )
            self.emotion_model = None
            self.multilingual_model = None
            self.compact_model = None
            logger.info("✅ Fallback модели загружены")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка загрузки моделей: {e}")
            # Устанавливаем все модели в None если ничего не работает
            self.sentiment_model = None
            self.emotion_model = None
            self.multilingual_model = None
            self.compact_model = None
    
    async def analyze_with_openrouter(self, text: str, model: str = "google/gemini-flash-1.5") -> Dict:
        """Анализ через OpenRouter API (бесплатные модели)"""
        if not self.openrouter_api_key:
            return {'success': False, 'error': 'OpenRouter API key not set'}
        
        try:
            prompt = f"""Проанализируй следующий текст на русском языке:

"{text}"

Определи:
1. Тональность (positive/negative/neutral) с уверенностью в %
2. Основные эмоции (радость, грусть, гнев, страх, удивление, отвращение, интерес, вина, стыд)
3. Личностные черты автора (Big Five: openness, conscientiousness, extraversion, agreeableness, neuroticism)
4. Ключевые темы и паттерны

Ответь в JSON формате:
{{
  "sentiment": {{"label": "...", "confidence": 0.85}},
  "emotions": {{"joy": 0.3, "sadness": 0.1, ...}},
  "personality": {{"openness": 0.7, "conscientiousness": 0.6, ...}},
  "themes": ["тема1", "тема2"],
  "insights": ["инсайт1", "инсайт2"]
}}"""

            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://oracul-bot.local",
                "X-Title": "Oracul Bot Local"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # Пытаемся парсить JSON из ответа
                        try:
                            import json
                            import re
                            
                            # Ищем JSON в ответе
                            json_match = re.search(r'\{.*\}', content, re.DOTALL)
                            if json_match:
                                analysis = json.loads(json_match.group())
                                return {
                                    'success': True,
                                    'analysis': analysis,
                                    'model_used': model,
                                    'raw_response': content
                                }
                            else:
                                return {
                                    'success': True,
                                    'analysis': {'raw_text': content},
                                    'model_used': model,
                                    'raw_response': content
                                }
                        except json.JSONDecodeError:
                            return {
                                'success': True,
                                'analysis': {'raw_text': content},
                                'model_used': model,
                                'raw_response': content
                            }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"OpenRouter API error {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"OpenRouter analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_with_modern_models(self, text: str) -> Dict:
        """Анализ с современными локальными моделями"""
        try:
            results = {}
            
            # 1. Современный анализ эмоций (9 эмоций)
            if hasattr(self, 'emotion_model') and self.emotion_model:
                emotion_results = self.emotion_model(text[:512])
                
                # Преобразуем в удобный формат
                emotions = {}
                emotion_labels = [
                    'neutral', 'joy', 'sadness', 'anger', 'enthusiasm', 
                    'surprise', 'disgust', 'fear', 'guilt', 'shame'
                ]
                
                if isinstance(emotion_results[0], list):
                    for emotion_data in emotion_results[0]:
                        label = emotion_data['label'].lower()
                        score = emotion_data['score']
                        emotions[label] = score
                
                results['modern_emotions'] = emotions
            
            # 2. Улучшенная тональность
            if hasattr(self, 'sentiment_model') and self.sentiment_model:
                sentiment_result = self.sentiment_model(text[:512])
                results['improved_sentiment'] = {
                    'label': sentiment_result[0]['label'].lower(),
                    'confidence': sentiment_result[0]['score']
                }
            
            # 3. Многоязычная модель для сравнения
            if hasattr(self, 'multilingual_model') and self.multilingual_model:
                multi_result = self.multilingual_model(text[:512])
                results['multilingual_sentiment'] = {
                    'label': self._normalize_sentiment_label(multi_result[0]['label']),
                    'confidence': multi_result[0]['score']
                }
            
            # 4. Компактная модель (быстрый анализ)
            if hasattr(self, 'compact_model') and self.compact_model:
                compact_result = self.compact_model(text[:512])
                results['compact_sentiment'] = {
                    'label': compact_result[0]['label'].lower(),
                    'confidence': compact_result[0]['score']
                }
            
            return {
                'success': True,
                'results': results,
                'models_used': list(results.keys())
            }
            
        except Exception as e:
            logger.error(f"Modern models analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _normalize_sentiment_label(self, label: str) -> str:
        """Нормализация меток тональности"""
        label = label.lower()
        if 'pos' in label or label in ['1', '4', '5']:
            return 'positive'
        elif 'neg' in label or label in ['0', '1']:
            return 'negative'
        else:
            return 'neutral'
    
    async def comprehensive_analysis(self, text: str, use_openrouter: bool = True) -> Dict:
        """Комплексный анализ с современными методами"""
        try:
            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'text_length': len(text),
                'analysis_methods': []
            }
            
            # 1. Анализ современными локальными моделями
            logger.info("Running modern local models analysis...")
            local_results = await self.analyze_with_modern_models(text)
            
            if local_results.get('success'):
                analysis_results['local_analysis'] = local_results['results']
                analysis_results['analysis_methods'].append('modern_local_models')
            
            # 2. Анализ через OpenRouter (если доступен)
            if use_openrouter and self.openrouter_api_key:
                logger.info("Running OpenRouter analysis...")
                
                # Пробуем разные бесплатные модели
                free_models = [
                    "google/gemini-flash-1.5",
                    "meta-llama/llama-3.2-3b-instruct:free",
                    "microsoft/phi-3-mini-128k-instruct:free",
                    "qwen/qwen-2-7b-instruct:free"
                ]
                
                for model in free_models:
                    openrouter_result = await self.analyze_with_openrouter(text, model)
                    if openrouter_result.get('success'):
                        analysis_results['openrouter_analysis'] = openrouter_result
                        analysis_results['analysis_methods'].append(f'openrouter_{model}')
                        break
            
            # 3. Генерируем сводный анализ
            summary = self._generate_comprehensive_summary(analysis_results)
            analysis_results['summary'] = summary
            
            return {
                'success': True,
                'analysis': analysis_results
            }
            
        except Exception as e:
            logger.error(f"Comprehensive analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_comprehensive_summary(self, results: Dict) -> Dict:
        """Генерация сводного анализа"""
        try:
            summary = {
                'methods_used': len(results.get('analysis_methods', [])),
                'confidence_level': 'high' if len(results.get('analysis_methods', [])) >= 2 else 'medium'
            }
            
            # Анализируем локальные результаты
            local_analysis = results.get('local_analysis', {})
            
            # Тональность (консенсус между моделями)
            sentiments = []
            if 'improved_sentiment' in local_analysis:
                sentiments.append(local_analysis['improved_sentiment'])
            if 'multilingual_sentiment' in local_analysis:
                sentiments.append(local_analysis['multilingual_sentiment'])
            if 'compact_sentiment' in local_analysis:
                sentiments.append(local_analysis['compact_sentiment'])
            
            if sentiments:
                # Находим консенсус
                sentiment_votes = {}
                total_confidence = 0
                
                for sent in sentiments:
                    label = sent['label']
                    confidence = sent['confidence']
                    
                    if label not in sentiment_votes:
                        sentiment_votes[label] = {'count': 0, 'confidence': 0}
                    
                    sentiment_votes[label]['count'] += 1
                    sentiment_votes[label]['confidence'] += confidence
                    total_confidence += confidence
                
                # Выбираем наиболее популярную тональность
                best_sentiment = max(sentiment_votes.items(), key=lambda x: x[1]['count'])
                avg_confidence = best_sentiment[1]['confidence'] / best_sentiment[1]['count']
                
                summary['consensus_sentiment'] = {
                    'label': best_sentiment[0],
                    'confidence': avg_confidence,
                    'agreement': best_sentiment[1]['count'] / len(sentiments)
                }
            
            # Эмоции (из современной модели)
            if 'modern_emotions' in local_analysis:
                emotions = local_analysis['modern_emotions']
                top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
                summary['top_emotions'] = top_emotions
            
            # OpenRouter инсайты
            openrouter_analysis = results.get('openrouter_analysis', {})
            if openrouter_analysis.get('success'):
                or_analysis = openrouter_analysis.get('analysis', {})
                if isinstance(or_analysis, dict):
                    summary['openrouter_insights'] = or_analysis.get('insights', [])
                    summary['openrouter_themes'] = or_analysis.get('themes', [])
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return {'error': str(e)}


# Список лучших бесплатных моделей OpenRouter 2024
OPENROUTER_FREE_MODELS = [
    "google/gemini-flash-1.5",  # Google's fast model
    "meta-llama/llama-3.2-3b-instruct:free",  # Meta's Llama
    "microsoft/phi-3-mini-128k-instruct:free",  # Microsoft's Phi
    "qwen/qwen-2-7b-instruct:free",  # Alibaba's Qwen
    "mistralai/mistral-7b-instruct:free",  # Mistral
    "huggingface/starcoder2-15b:free",  # Code-focused
    "openchat/openchat-7b:free",  # OpenChat
    "teknium/openhermes-2.5-mistral-7b:free",  # OpenHermes
]

# Современные модели Hugging Face для русского языка
MODERN_RUSSIAN_MODELS = {
    'emotion': [
        "Djacon/rubert-tiny2-russian-emotion-detection",  # 9 эмоций, 2023
        "cointegrated/rubert-tiny2-cedr-emotion-detection",  # Multilabel эмоции
    ],
    'sentiment': [
        "sismetanin/rubert-ru-sentiment-rusentiment",  # VK данные
        "seara/rubert-tiny2-russian-sentiment",  # Компактная модель
        "nlptown/bert-base-multilingual-uncased-sentiment",  # Многоязычная
    ],
    'classification': [
        "cointegrated/rubert-tiny2",  # Базовая модель для fine-tuning
        "DeepPavlov/rubert-base-cased-sentence",  # Эмбеддинги
    ]
}
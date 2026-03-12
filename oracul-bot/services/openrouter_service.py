"""
OpenRouter API сервис для доступа к бесплатным LLM моделям
"""

import logging
import asyncio
import aiohttp
import json
import os
import re
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Импортируем промпты
from prompts import AnalysisPrompts, SystemPrompts

# Загружаем переменные окружения
load_dotenv()

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Сервис для работы с OpenRouter API"""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.app_name = "Oracul Bot Local"
        self.site_url = "https://oracul-bot.local"
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Настроенные модели из .env файла
        self.default_model = os.getenv('DEFAULT_MODEL', 'openai/gpt-oss-120b:free')
        self.backup_model = os.getenv('BACKUP_MODEL', 'openai/gpt-oss-20b:free')
        self.third_model = os.getenv('THIRD_MODEL', 'nvidia/nemotron-3-nano-30b-a3b:free')
        self.fourth_model = os.getenv('FOURTH_MODEL', 'arcee-ai/trinity-mini:free')
        
        # Приоритетный список: 4 модели (актуальные данные OpenRouter декабрь 2024)
        # 1-2: gpt-oss (лучшее качество, могут быть rate limits)
        # 3: nvidia/nemotron - баланс throughput/latency (256k контекст, 30B параметров)
        # 4: arcee-ai/trinity - баланс throughput/latency (131k контекст)
        self.free_models = [
            self.default_model,  # openai/gpt-oss-120b:free - 131k контекст, 120B параметров
            self.backup_model,   # openai/gpt-oss-20b:free - 131k контекст, 20B параметров
            self.third_model,    # nvidia/nemotron-3-nano-30b-a3b:free - 256k контекст, 30B параметров
            self.fourth_model    # arcee-ai/trinity-mini:free - 131k контекст, оптимизированная
        ]
        
        # Специализированные модели (используем только из топ-4)
        self.specialized_models = {
            'analysis': self.default_model,  # gpt-oss-120b для глубокого анализа
            'coding': self.backup_model,  # gpt-oss-20b для кода
            'reasoning': self.default_model,  # gpt-oss-120b для рассуждений
            'creative': self.backup_model,  # gpt-oss-20b для творчества
            'fast': self.third_model  # nvidia/nemotron для быстрых ответов
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать переиспользуемую HTTP-сессию"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.app_name
                }
            )
        return self._session

    async def close(self):
        """Закрыть HTTP-сессию"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_available_models(self) -> List[Dict]:
        """Получить список доступных моделей"""
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.base_url}/models",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    logger.error(f"Failed to get models: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    async def analyze_text(self, text: str, task_type: str = 'analysis') -> Dict:
        """Анализ текста через OpenRouter с обработкой rate limits"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'OpenRouter API key not configured'
            }
        
        try:
            # Выбираем подходящую модель
            primary_model = self.specialized_models.get(task_type, self.free_models[0])
            
            # Создаем промпт для анализа
            prompt = self._create_analysis_prompt(text, task_type)
            
            # Пытаемся с основной моделью
            result = await self._make_request_with_fallback(primary_model, prompt)
            
            if result.get('success'):
                # Парсим результат
                parsed_result = self._parse_analysis_result(result['content'])
                
                return {
                    'success': True,
                    'analysis': parsed_result,
                    'model_used': result.get('model_used', primary_model),
                    'task_type': task_type,
                    'raw_response': result['content']
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Text analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_analysis_prompt(self, text: str, task_type: str) -> str:
        """Создание промпта для анализа"""
        return AnalysisPrompts.get_text_analysis_prompt(text, task_type)
    
    async def _make_request_with_fallback(self, primary_model: str, prompt: str, max_tokens: int = 1500) -> Dict:
        """Выполнение запроса с автоматическим переключением моделей при rate limit"""
        models_to_try = [primary_model] + [m for m in self.free_models if m != primary_model]
        
        for i, model in enumerate(models_to_try):
            try:
                logger.info(f"Попытка {i+1}: используем модель {model}")
                result = await self._make_request(model, prompt, max_tokens)
                
                if result.get('success'):
                    result['model_used'] = model
                    if i > 0:
                        logger.info(f"✅ Успешно переключились на модель {model}")
                    return result
                
                # Проверяем тип ошибки
                status_code = result.get('status_code', 0)
                error_msg = result.get('error', '').lower()
                
                # Rate limit - пробуем следующую модель
                if status_code == 429 or 'rate limit' in error_msg or 'quota' in error_msg:
                    logger.warning(f"⚠️ Rate limit для модели {model}, переключаемся...")
                    if i < len(models_to_try) - 1:
                        await asyncio.sleep(1)  # Небольшая пауза
                        continue
                
                # Другие ошибки - тоже пробуем следующую модель
                logger.warning(f"⚠️ Ошибка модели {model}: {result.get('error')}")
                if i < len(models_to_try) - 1:
                    await asyncio.sleep(0.5)
                    continue
                
                # Если это последняя модель, возвращаем ошибку
                return result
                
            except Exception as e:
                logger.error(f"❌ Критическая ошибка модели {model}: {e}")
                if i < len(models_to_try) - 1:
                    continue
                return {
                    'success': False,
                    'error': f'All models failed. Last error: {str(e)}'
                }
        
        return {
            'success': False,
            'error': 'No models available'
        }

    async def _make_request(self, model: str, prompt: str, max_tokens: int = 1500) -> Dict:
        """Выполнение запроса к OpenRouter API"""
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": max_tokens,
                "top_p": 0.9
            }

            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']

                    return {
                        'success': True,
                        'content': content,
                        'usage': result.get('usage', {}),
                        'model': model
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"OpenRouter API error {response.status}: {error_text}")

                    return {
                        'success': False,
                        'error': f"API error {response.status}: {error_text}",
                        'status_code': response.status
                    }

        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': 'Request timeout (60s)'
            }
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_analysis_result(self, content: str) -> Dict:
        """Парсинг результата анализа"""
        try:
            logger.info(f"🔍 Парсинг ответа OpenRouter (длина: {len(content)} символов)")
            logger.info(f"📄 Первые 200 символов ответа: {content[:200]}")
            
            # Пытаемся найти JSON в ответе
            
            # Ищем JSON блок
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                logger.info(f"📄 Найден JSON блок (длина: {len(json_str)} символов)")
                try:
                    parsed = json.loads(json_str)
                    logger.info(f"✅ JSON успешно распарсен, ключи: {list(parsed.keys())}")
                    
                    # Проверяем, что JSON содержит полезные данные
                    if any(key in parsed for key in ['sentiment', 'themes', 'insights', 'emotions']):
                        return parsed
                    else:
                        logger.warning("⚠️ JSON не содержит ожидаемых ключей, парсим как текст")
                        return self._parse_text_response(content)
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ JSON невалидный: {e}, пытаемся исправить")
                    # Если JSON невалидный, пытаемся исправить
                    fixed_result = self._fix_and_parse_json(json_str)
                    if 'parse_error' not in fixed_result:
                        return fixed_result
                    else:
                        logger.warning("⚠️ Не удалось исправить JSON, парсим как текст")
                        return self._parse_text_response(content)
            
            logger.warning("⚠️ JSON не найден в ответе, парсим как текст")
            # Если JSON не найден, парсим текстовый ответ
            return self._parse_text_response(content)
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга: {e}")
            return {
                'raw_text': content,
                'parse_error': str(e)
            }
    
    def _fix_and_parse_json(self, json_str: str) -> Dict:
        """Попытка исправить и парсить поврежденный JSON"""
        try:
            # Базовые исправления
            json_str = json_str.replace("'", '"')  # Одинарные кавычки
            json_str = re.sub(r',\s*}', '}', json_str)  # Лишние запятые
            json_str = re.sub(r',\s*]', ']', json_str)  # Лишние запятые в массивах
            
            parsed = json.loads(json_str)
            logger.info("✅ JSON успешно исправлен и распарсен")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Не удалось исправить JSON: {e}")
            # Если все еще не парсится, возвращаем как текст
            return {'raw_text': json_str, 'parse_error': str(e)}
    
    def _parse_text_response(self, content: str) -> Dict:
        """Парсинг текстового ответа"""
        try:
            result = {'raw_text': content}
            
            logger.info(f"📝 Парсинг текстового ответа (длина: {len(content)})")
            
            # Ищем тональность
            sentiment_patterns = [
                r'тональность[:\s]*([a-zA-Zа-яё]+)',
                r'sentiment[:\s]*([a-zA-Z]+)',
                r'(positive|negative|neutral|позитивн|негативн|нейтральн)'
            ]
            
            for pattern in sentiment_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    sentiment = match.group(1).lower()
                    if 'позитивн' in sentiment or 'positive' in sentiment:
                        result['sentiment'] = {'label': 'positive', 'confidence': 0.7}
                    elif 'негативн' in sentiment or 'negative' in sentiment:
                        result['sentiment'] = {'label': 'negative', 'confidence': 0.7}
                    else:
                        result['sentiment'] = {'label': 'neutral', 'confidence': 0.7}
                    break
            
            # Ищем эмоции
            emotions = ['радость', 'грусть', 'гнев', 'страх', 'удивление', 'отвращение', 'интерес']
            found_emotions = []
            
            for emotion in emotions:
                if emotion in content.lower():
                    found_emotions.append(emotion)
            
            if found_emotions:
                result['emotions'] = found_emotions
            
            # Ищем темы
            themes = []
            theme_patterns = [
                r'тем[аы][:\s]*([^\n]+)',
                r'themes?[:\s]*([^\n]+)',
                r'ключев[ыие][е]?\s+тем[аы][:\s]*([^\n]+)'
            ]
            
            for pattern in theme_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Разбиваем по запятым и очищаем
                    topics = [t.strip() for t in match.split(',') if t.strip()]
                    themes.extend(topics[:3])  # Максимум 3 темы
            
            if themes:
                result['themes'] = themes[:5]  # Максимум 5 тем
            
            # Ищем инсайты
            insights = []
            insight_patterns = [
                r'инсайт[ы]?[:\s]*([^\n]+)',
                r'insights?[:\s]*([^\n]+)',
                r'наблюдени[ея][:\s]*([^\n]+)',
                r'вывод[ы]?[:\s]*([^\n]+)'
            ]
            
            for pattern in insight_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                insights.extend([m.strip() for m in matches if m.strip()])
            
            # Также ищем пункты списка
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith(('•', '-', '*', '1.', '2.', '3.')) and len(line) > 10:
                    clean_line = re.sub(r'^[•\-*\d\.]\s*', '', line).strip()
                    if clean_line and len(clean_line) > 5:
                        insights.append(clean_line)
            
            if insights:
                result['insights'] = insights[:5]  # Первые 5
            
            # Ищем паттерны
            patterns = []
            pattern_keywords = ['паттерн', 'pattern', 'закономерность', 'тенденция']
            
            for line in lines:
                if any(keyword in line.lower() for keyword in pattern_keywords):
                    clean_line = line.strip()
                    if len(clean_line) > 10:
                        patterns.append(clean_line)
            
            if patterns:
                result['patterns'] = patterns[:3]
            
            # Если ничего не нашли, создаем базовые инсайты
            if not result.get('insights') and not result.get('themes'):
                result['insights'] = [
                    "Проанализирован текстовый контент",
                    "Обнаружены коммуникационные паттерны",
                    "Выявлены особенности стиля общения"
                ]
                result['themes'] = ["общение", "диалог", "взаимодействие"]
            
            logger.info(f"✅ Извлечено из текста: темы={len(result.get('themes', []))}, инсайты={len(result.get('insights', []))}")
            
            return result
            
        except Exception as e:
            logger.error(f"Text parsing error: {e}")
            return {
                'raw_text': content, 
                'parse_error': str(e),
                'insights': ["Анализ завершен, но возникла ошибка парсинга"],
                'themes': ["общий анализ"]
            }
    
    async def test_connection(self) -> Dict:
        """Тест соединения с OpenRouter с fallback"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'API key not configured'
                }
            
            # Простой тест запрос с fallback
            result = await self._make_request_with_fallback(
                primary_model=self.free_models[0],
                prompt="Привет! Это тест соединения. Ответь кратко 'OK'.",
                max_tokens=50
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'message': 'OpenRouter connection successful',
                    'model_tested': result.get('model_used', 'unknown'),
                    'response': result['content'][:100]
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection test failed: {e}'
            }
    
    async def get_model_info(self, model_name: str) -> Dict:
        """Получить информацию о модели"""
        try:
            models = await self.get_available_models()
            
            for model in models:
                if model.get('id') == model_name:
                    return {
                        'success': True,
                        'model_info': model
                    }
            
            return {
                'success': False,
                'error': f'Model {model_name} not found'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_recommended_model(self, task_type: str, text_length: int = 0) -> str:
        """Получить рекомендуемую модель для задачи с учетом производительности"""
        
        # Для очень длинных текстов - модели с большим контекстом
        if text_length > 4000:
            return "microsoft/phi-3-mini-128k-instruct:free"  # 128k контекст
        
        # Для быстрых задач - самые быстрые модели
        if task_type == 'fast' or text_length < 100:
            return "meta-llama/llama-3.2-3b-instruct:free"  # 3B параметров = высокая скорость
        
        # Для анализа и рассуждений - лучшее качество
        if task_type in ['analysis', 'reasoning']:
            return self.default_model  # nvidia/nemotron-3-nano-30b-a3b:free
        
        # Для кода - специализированная модель
        if task_type == 'coding':
            return "microsoft/phi-3-mini-128k-instruct:free"
        
        # Для творчества - Llama
        if task_type == 'creative':
            return "meta-llama/llama-3.2-3b-instruct:free"
        
        # По умолчанию лучшая универсальная модель
        return self.default_model
    
    def get_performance_info(self) -> Dict:
        """Получить информацию о производительности моделей (топ-4, актуальные данные)"""
        return {
            'priority_order': [
                "openai/gpt-oss-120b:free",  # Приоритет 1
                "openai/gpt-oss-20b:free",   # Приоритет 2
                "nvidia/nemotron-3-nano-30b-a3b:free",  # Приоритет 3
                "arcee-ai/trinity-mini:free"  # Приоритет 4
            ],
            'model_characteristics': {
                'openai/gpt-oss-120b:free': '120B параметров, 131k контекст, лучшее качество (rate limit возможен)',
                'openai/gpt-oss-20b:free': '20B параметров, 131k контекст, хорошее качество (rate limit возможен)',
                'nvidia/nemotron-3-nano-30b-a3b:free': '30B параметров, 256k контекст, баланс throughput/latency',
                'arcee-ai/trinity-mini:free': '131k контекст, оптимизированная для баланса throughput/latency'
            },
            'throughput_latency_balance': [
                'nvidia/nemotron-3-nano-30b-a3b:free',  # Лучший баланс
                'arcee-ai/trinity-mini:free'  # Оптимизированная
            ],
            'fallback_strategy': 'При rate limit: gpt-oss-120b → gpt-oss-20b → nemotron-30b → trinity-mini',
            'recommended_default': self.default_model,
            'data_source': 'OpenRouter API (декабрь 2024)',
            'selection_criteria': 'gpt-oss для качества, nemotron+trinity для баланса throughput/latency'
        }


# Глобальный экземпляр сервиса
openrouter_service = OpenRouterService()


# Конфигурация для .env файла
OPENROUTER_CONFIG_TEMPLATE = """
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Получить бесплатный API ключ:
# 1. Зарегистрируйтесь на https://openrouter.ai/
# 2. Получите $5 бесплатных кредитов
# 3. Скопируйте API ключ в настройки
# 4. Многие модели полностью бесплатные!

# Лучшие бесплатные модели 2024:
# - google/gemini-flash-1.5 (быстрый и качественный)
# - meta-llama/llama-3.2-3b-instruct:free (Meta)
# - microsoft/phi-3-mini-128k-instruct:free (большой контекст)
# - qwen/qwen-2-7b-instruct:free (Alibaba)
"""
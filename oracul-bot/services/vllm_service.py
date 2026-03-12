"""
Сервис для работы с vLLM сервером
Обеспечивает высокопроизводительный inference локальных LLM
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class VLLMService:
    """Сервис для работы с vLLM API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate(
        self,
        prompt: str,
        model: str = "microsoft/DialoGPT-medium",
        max_tokens: int = 150,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> Dict:
        """
        Генерация текста через vLLM API
        
        Args:
            prompt: Входной промпт
            model: Название модели
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации
            top_p: Top-p sampling
            stop: Стоп-последовательности
            
        Returns:
            Dict с результатом генерации
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": False
            }
            
            if stop:
                payload["stop"] = stop
            
            async with self.session.post(
                f"{self.base_url}/v1/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'text': result['choices'][0]['text'],
                        'model': model,
                        'usage': result.get('usage', {})
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"vLLM API error {response.status}: {error_text}")
                    return {
                        'success': False,
                        'error': f"API error: {response.status}"
                    }
                    
        except asyncio.TimeoutError:
            logger.error("vLLM API timeout")
            return {
                'success': False,
                'error': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"vLLM service error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "microsoft/DialoGPT-medium",
        max_tokens: int = 150,
        temperature: float = 0.7
    ) -> Dict:
        """
        Chat completion через vLLM API
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            model: Название модели
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации
            
        Returns:
            Dict с результатом
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            async with self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'message': result['choices'][0]['message']['content'],
                        'model': model,
                        'usage': result.get('usage', {})
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"vLLM Chat API error {response.status}: {error_text}")
                    return {
                        'success': False,
                        'error': f"Chat API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"vLLM chat service error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_text_with_llm(self, text: str, analysis_type: str = "general") -> Dict:
        """
        Анализ текста с помощью локальной LLM через vLLM
        
        Args:
            text: Текст для анализа
            analysis_type: Тип анализа (general, emotion, personality)
            
        Returns:
            Dict с результатами анализа
        """
        try:
            # Формируем промпт в зависимости от типа анализа
            if analysis_type == "emotion":
                prompt = f"""
Проанализируй эмоциональное содержание следующего текста:

"{text}"

Определи:
1. Основные эмоции (радость, грусть, гнев, страх, удивление)
2. Интенсивность эмоций (низкая/средняя/высокая)
3. Общее эмоциональное состояние

Ответ дай в структурированном виде.
"""
            elif analysis_type == "personality":
                prompt = f"""
Проанализируй личностные особенности автора по тексту:

"{text}"

Определи тенденции:
1. Открытость новому опыту
2. Добросовестность
3. Экстраверсия
4. Доброжелательность
5. Эмоциональная стабильность

Ответ дай кратко и структурированно.
"""
            else:  # general
                prompt = f"""
Проанализируй следующий текст:

"{text}"

Дай краткий анализ:
1. Основная тема
2. Эмоциональная окраска
3. Стиль изложения
4. Ключевые особенности

Будь объективен и конкретен.
"""
            
            # Генерируем анализ
            result = await self.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3,
                stop=["\n\n", "---"]
            )
            
            if result['success']:
                return {
                    'success': True,
                    'analysis': result['text'].strip(),
                    'analysis_type': analysis_type,
                    'model_used': result.get('model', 'unknown')
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"LLM text analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def health_check(self) -> bool:
        """Проверка доступности vLLM сервера"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.base_url}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"vLLM health check error: {e}")
            return False
    
    async def get_models(self) -> List[str]:
        """Получить список доступных моделей"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.base_url}/v1/models",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return [model['id'] for model in result.get('data', [])]
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Get models error: {e}")
            return []


# Глобальный экземпляр сервиса
vllm_service = VLLMService()


async def analyze_with_vllm(text: str, analysis_type: str = "general") -> Dict:
    """
    Удобная функция для анализа текста с vLLM
    
    Args:
        text: Текст для анализа
        analysis_type: Тип анализа
        
    Returns:
        Dict с результатами
    """
    async with VLLMService() as service:
        return await service.analyze_text_with_llm(text, analysis_type)
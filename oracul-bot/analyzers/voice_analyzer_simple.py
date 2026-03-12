"""
Упрощенный анализатор голоса для Oracul Bot (без librosa)
"""

import logging
import asyncio
import tempfile
import os
from typing import Dict, Optional
import openai

from config.settings import settings

logger = logging.getLogger(__name__)


class VoiceAnalyzer:
    """Упрощенный анализатор голосовых сообщений"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze(self, voice_file, duration: float, user_context: Optional[Dict] = None) -> Dict:
        """
        Упрощенный анализ голосового сообщения
        
        Args:
            voice_file: Файл голосового сообщения
            duration: Длительность в секундах
            user_context: Контекст пользователя
            
        Returns:
            Dict с результатами анализа
        """
        try:
            # Скачиваем и сохраняем файл временно
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                await voice_file.download_media(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Только транскрипция и анализ содержания
                result = await self._transcribe_and_analyze(temp_path, user_context)
                
                # Добавляем базовые характеристики на основе длительности
                audio_features = self._analyze_duration_features(duration)
                
                analysis = {
                    'success': True,
                    'duration': duration,
                    'audio_features': audio_features,
                    'transcription_analysis': result,
                    'recommendations': []
                }
                
                # Генерируем рекомендации
                analysis['recommendations'] = await self._generate_voice_recommendations(analysis)
                
                return analysis
                
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error in voice analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_duration_features(self, duration: float) -> Dict:
        """Анализ характеристик на основе длительности"""
        interpretation = {}
        
        # Анализ темпа на основе длительности
        if duration > 60:  # Длинное сообщение
            interpretation['pace'] = 'медленный'
            interpretation['speech_pattern'] = 'подробная речь'
            interpretation['emotional_state'] = 'обдуманное'
        elif duration > 30:  # Среднее сообщение
            interpretation['pace'] = 'нормальный'
            interpretation['speech_pattern'] = 'обычная речь'
            interpretation['emotional_state'] = 'спокойное'
        elif duration > 10:  # Короткое сообщение
            interpretation['pace'] = 'быстрый'
            interpretation['speech_pattern'] = 'краткая речь'
            interpretation['emotional_state'] = 'активное'
        else:  # Очень короткое
            interpretation['pace'] = 'очень быстрый'
            interpretation['speech_pattern'] = 'импульсивная речь'
            interpretation['emotional_state'] = 'эмоциональное'
        
        # Энергия на основе длительности (эвристика)
        if duration < 5:
            interpretation['energy_level'] = 'высокая'
        elif duration < 20:
            interpretation['energy_level'] = 'средняя'
        else:
            interpretation['energy_level'] = 'низкая'
        
        return {
            'interpretation': interpretation,
            'duration_analysis': {
                'category': 'short' if duration < 15 else 'medium' if duration < 45 else 'long',
                'estimated_words': int(duration * 2.5)  # Примерно 2.5 слова в секунду
            }
        }
    
    async def _transcribe_and_analyze(self, audio_path: str, user_context: Optional[Dict] = None) -> Dict:
        """Транскрипция и анализ содержания"""
        try:
            # Транскрибируем аудио
            with open(audio_path, 'rb') as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru"
                )
            
            text = transcript.text
            
            if not text or len(text.strip()) < 5:
                return {'transcription': '', 'analysis': {}}
            
            # Анализируем содержание с помощью LLM
            context_info = ""
            if user_context:
                context_info = f"Контекст пользователя: {user_context.get('summary', '')}\n"
            
            prompt = f"""
Проанализируй голосовое сообщение пользователя:

{context_info}
Транскрипция: "{text}"

Проанализируй:
1. Эмоциональное состояние по содержанию
2. Уровень стресса или напряжения
3. Основные темы и заботы
4. Тон общения (формальный/неформальный/дружеский)
5. Потребности или запросы

Ответь в формате JSON:
{{
    "emotional_tone": "описание эмоционального тона",
    "stress_level": "низкий/средний/высокий",
    "main_topics": ["тема1", "тема2"],
    "communication_style": "описание стиля",
    "detected_needs": ["потребность1", "потребность2"],
    "overall_mood": "описание общего настроения"
}}
            """
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты эксперт по анализу речи и эмоций. Анализируй деликатно и профессионально."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            # Парсим JSON ответ
            import json
            content_analysis = json.loads(response.choices[0].message.content)
            
            return {
                'transcription': text,
                'content_analysis': content_analysis
            }
            
        except Exception as e:
            logger.error(f"Transcription and analysis error: {e}")
            return {'transcription': '', 'analysis': {}}
    
    async def _generate_voice_recommendations(self, analysis: Dict) -> list:
        """Генерация рекомендаций на основе анализа голоса"""
        recommendations = []
        
        try:
            audio_features = analysis.get('audio_features', {})
            transcription_analysis = analysis.get('transcription_analysis', {})
            
            interpretation = audio_features.get('interpretation', {})
            content_analysis = transcription_analysis.get('content_analysis', {})
            
            # Рекомендации на основе длительности
            duration = analysis.get('duration', 0)
            if duration > 60:
                recommendations.append("Длинные сообщения показывают вдумчивость - это хорошо!")
            elif duration < 5:
                recommendations.append("Короткие сообщения могут указывать на эмоциональность")
            
            # Рекомендации на основе содержания
            if content_analysis.get('stress_level') == 'высокий':
                recommendations.append("Высокий уровень стресса в речи - попробуй техники релаксации")
            
            if content_analysis.get('overall_mood') and 'позитив' in content_analysis['overall_mood'].lower():
                recommendations.append("Отличное настроение слышно в голосе - продолжай в том же духе!")
            
            # Общие рекомендации
            if not recommendations:
                recommendations.append("Твой голос многое говорит о тебе - продолжай развивать эмоциональный интеллект")
            
            return recommendations[:4]  # Максимум 4 рекомендации
            
        except Exception as e:
            logger.error(f"Voice recommendations generation error: {e}")
            return ["Анализ голоса помогает лучше понять эмоциональное состояние"]
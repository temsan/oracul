"""
Сервис анализа для Oracul Bot
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Analysis, AnalysisType, User
from database.connection import get_session
from analyzers.text_analyzer import TextAnalyzer
from analyzers.voice_analyzer import VoiceAnalyzer

logger = logging.getLogger(__name__)


class AnalysisService:
    """Сервис для выполнения различных типов анализа"""
    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()
        self.voice_analyzer = VoiceAnalyzer()
    
    async def analyze_text(self, user_id: int, text: str) -> Dict:
        """Анализ текстового сообщения"""
        try:
            # Получаем контекст пользователя
            user_context = await self._get_user_context(user_id)
            
            # Выполняем анализ
            result = await self.text_analyzer.analyze(text, user_context)
            
            if result['success']:
                # Сохраняем результат в БД
                await self._save_analysis(
                    user_id=user_id,
                    analysis_type=AnalysisType.TEXT,
                    input_data={'text': text},
                    results=result,
                    summary=self._generate_text_summary(result),
                    recommendations=result.get('recommendations', [])
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Text analysis service error: {e}")
            return {
                'success': False,
                'error': 'Ошибка при анализе текста'
            }
    
    async def analyze_voice(self, user_id: int, voice_file, duration: float) -> Dict:
        """Анализ голосового сообщения"""
        try:
            # Получаем контекст пользователя
            user_context = await self._get_user_context(user_id)
            
            # Выполняем анализ
            result = await self.voice_analyzer.analyze(voice_file, duration, user_context)
            
            if result['success']:
                # Сохраняем результат в БД
                await self._save_analysis(
                    user_id=user_id,
                    analysis_type=AnalysisType.VOICE,
                    input_data={'duration': duration},
                    results=result,
                    summary=self._generate_voice_summary(result),
                    recommendations=result.get('recommendations', [])
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Voice analysis service error: {e}")
            return {
                'success': False,
                'error': 'Ошибка при анализе голоса'
            }
    
    async def get_user_analyses(self, user_id: int, limit: int = 10) -> list:
        """Получить последние анализы пользователя"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, desc
                
                result = await session.execute(
                    select(Analysis)
                    .where(Analysis.user_id == user_id)
                    .order_by(desc(Analysis.created_at))
                    .limit(limit)
                )
                
                analyses = result.scalars().all()
                
                return [
                    {
                        'id': analysis.id,
                        'type': analysis.analysis_type.value,
                        'summary': analysis.summary,
                        'created_at': analysis.created_at.isoformat(),
                        'confidence_score': analysis.confidence_score,
                        'is_favorite': analysis.is_favorite
                    }
                    for analysis in analyses
                ]
                
        except Exception as e:
            logger.error(f"Get user analyses error: {e}")
            return []
    
    async def get_analysis_details(self, analysis_id: int, user_id: int) -> Optional[Dict]:
        """Получить детали конкретного анализа"""
        try:
            async with get_session() as session:
                from sqlalchemy import select
                
                result = await session.execute(
                    select(Analysis)
                    .where(Analysis.id == analysis_id, Analysis.user_id == user_id)
                )
                
                analysis = result.scalar_one_or_none()
                
                if not analysis:
                    return None
                
                return {
                    'id': analysis.id,
                    'type': analysis.analysis_type.value,
                    'input_data': analysis.input_data,
                    'results': analysis.results,
                    'summary': analysis.summary,
                    'recommendations': analysis.recommendations,
                    'confidence_score': analysis.confidence_score,
                    'processing_time': analysis.processing_time,
                    'created_at': analysis.created_at.isoformat(),
                    'is_favorite': analysis.is_favorite
                }
                
        except Exception as e:
            logger.error(f"Get analysis details error: {e}")
            return None
    
    async def _get_user_context(self, user_id: int) -> Dict:
        """Получить контекст пользователя для улучшения анализа"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, desc
                
                # Получаем последние анализы для контекста
                result = await session.execute(
                    select(Analysis)
                    .where(Analysis.user_id == user_id)
                    .order_by(desc(Analysis.created_at))
                    .limit(5)
                )
                
                recent_analyses = result.scalars().all()
                
                if not recent_analyses:
                    return {}
                
                # Формируем краткий контекст
                context = {
                    'total_analyses': len(recent_analyses),
                    'recent_types': [a.analysis_type.value for a in recent_analyses],
                    'summary': 'Пользователь регулярно использует анализ для самопознания'
                }
                
                return context
                
        except Exception as e:
            logger.error(f"Get user context error: {e}")
            return {}
    
    async def _save_analysis(
        self,
        user_id: int,
        analysis_type: AnalysisType,
        input_data: Dict,
        results: Dict,
        summary: str,
        recommendations: list,
        processing_time: Optional[float] = None
    ):
        """Сохранить результат анализа в БД"""
        try:
            async with get_session() as session:
                # Вычисляем confidence score
                confidence_score = self._calculate_confidence_score(results)
                
                analysis = Analysis(
                    user_id=user_id,
                    analysis_type=analysis_type,
                    input_data=input_data,
                    results=results,
                    summary=summary,
                    recommendations=recommendations,
                    confidence_score=confidence_score,
                    processing_time=processing_time
                )
                
                session.add(analysis)
                await session.commit()
                
                logger.info(f"Analysis saved for user {user_id}, type: {analysis_type.value}")
                
        except Exception as e:
            logger.error(f"Save analysis error: {e}")
    
    def _calculate_confidence_score(self, results: Dict) -> float:
        """Вычислить уверенность в результатах анализа"""
        try:
            confidence_factors = []
            
            # Для текстового анализа
            if 'sentiment' in results:
                sentiment_conf = results['sentiment'].get('confidence', 0)
                confidence_factors.append(sentiment_conf)
            
            # Для голосового анализа
            if 'audio_features' in results:
                # Простая эвристика на основе наличия данных
                audio_conf = 0.8 if results['audio_features'] else 0.3
                confidence_factors.append(audio_conf)
            
            if 'llm_analysis' in results and results['llm_analysis']:
                confidence_factors.append(0.9)  # LLM анализ обычно надежен
            
            # Возвращаем среднее или базовое значение
            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            
        except Exception as e:
            logger.error(f"Calculate confidence score error: {e}")
            return 0.5
    
    def _generate_text_summary(self, analysis_result: Dict) -> str:
        """Генерация краткого резюме текстового анализа"""
        try:
            sentiment = analysis_result.get('sentiment', {})
            emotions = analysis_result.get('emotions', {})
            
            summary_parts = []
            
            # Тональность
            if sentiment.get('label'):
                tone = sentiment['label']
                confidence = sentiment.get('confidence', 0) * 100
                summary_parts.append(f"Тональность: {tone} ({confidence:.0f}%)")
            
            # Доминирующие эмоции
            if emotions:
                top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
                emotion_strs = [f"{emotion}: {score*100:.0f}%" for emotion, score in top_emotions if score > 0.3]
                if emotion_strs:
                    summary_parts.append(f"Эмоции: {', '.join(emotion_strs)}")
            
            return "; ".join(summary_parts) if summary_parts else "Анализ текстового сообщения"
            
        except Exception as e:
            logger.error(f"Generate text summary error: {e}")
            return "Анализ текстового сообщения"
    
    def _generate_voice_summary(self, analysis_result: Dict) -> str:
        """Генерация краткого резюме анализа голоса"""
        try:
            audio_features = analysis_result.get('audio_features', {})
            transcription_analysis = analysis_result.get('transcription_analysis', {})
            
            summary_parts = []
            
            # Характеристики голоса
            interpretation = audio_features.get('interpretation', {})
            if interpretation.get('emotional_state'):
                summary_parts.append(f"Состояние: {interpretation['emotional_state']}")
            
            if interpretation.get('energy_level'):
                summary_parts.append(f"Энергия: {interpretation['energy_level']}")
            
            # Анализ содержания
            content_analysis = transcription_analysis.get('content_analysis', {})
            if content_analysis.get('overall_mood'):
                summary_parts.append(f"Настроение: {content_analysis['overall_mood']}")
            
            return "; ".join(summary_parts) if summary_parts else "Анализ голосового сообщения"
            
        except Exception as e:
            logger.error(f"Generate voice summary error: {e}")
            return "Анализ голосового сообщения"
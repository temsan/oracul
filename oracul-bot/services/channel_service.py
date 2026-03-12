"""
Сервис анализа каналов для Oracul Bot
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional
import os

from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Analysis, AnalysisType
from database.connection import get_session
from analyzers.channel_analyzer import ChannelAnalyzer
from config.settings import settings

logger = logging.getLogger(__name__)


class ChannelService:
    """Сервис для анализа Telegram каналов и групп"""
    
    def __init__(self):
        self.channel_analyzer = ChannelAnalyzer()
        self._initialized = False
    
    async def initialize(self):
        """Инициализация Telethon клиента"""
        if self._initialized:
            return True
        
        try:
            # Получаем данные для Telethon из переменных окружения
            api_id = os.getenv('TELEGRAM_API_ID')
            api_hash = os.getenv('TELEGRAM_API_HASH')
            phone = os.getenv('TELEGRAM_PHONE')
            
            if not api_id or not api_hash:
                logger.warning("Telegram API credentials not found. Channel analysis will be limited.")
                return False
            
            success = await self.channel_analyzer.initialize_client(
                api_id=int(api_id),
                api_hash=api_hash,
                phone=phone
            )
            
            self._initialized = success
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize channel service: {e}")
            return False
    
    async def analyze_channel(self, user_id: int, channel_input: str) -> Dict:
        """
        Анализ канала или группы
        
        Args:
            user_id: ID пользователя
            channel_input: Ссылка на канал или username
            
        Returns:
            Dict с результатами анализа
        """
        try:
            # Инициализируем клиент если нужно
            if not self._initialized:
                initialized = await self.initialize()
                if not initialized:
                    return {
                        'success': False,
                        'error': 'Сервис анализа каналов временно недоступен'
                    }
            
            # Получаем контекст пользователя
            user_context = await self._get_user_context(user_id)
            
            # Выполняем анализ
            result = await self.channel_analyzer.analyze_channel(
                channel_username=channel_input,
                message_limit=100
            )
            
            if result['success']:
                # Сохраняем результат в БД
                await self._save_channel_analysis(
                    user_id=user_id,
                    channel_input=channel_input,
                    analysis_result=result
                )
                
                return {
                    'success': True,
                    'analysis': result
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Channel analysis service error: {e}")
            return {
                'success': False,
                'error': 'Ошибка при анализе канала'
            }
    
    async def _get_user_context(self, user_id: int) -> Dict:
        """Получить контекст пользователя"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, desc
                
                # Получаем последние анализы каналов
                result = await session.execute(
                    select(Analysis)
                    .where(
                        Analysis.user_id == user_id,
                        Analysis.analysis_type == AnalysisType.BEHAVIORAL  # Используем для каналов
                    )
                    .order_by(desc(Analysis.created_at))
                    .limit(3)
                )
                
                recent_analyses = result.scalars().all()
                
                return {
                    'previous_channel_analyses': len(recent_analyses),
                    'user_experience': 'experienced' if len(recent_analyses) > 2 else 'beginner'
                }
                
        except Exception as e:
            logger.error(f"Get user context error: {e}")
            return {}
    
    async def _save_channel_analysis(
        self,
        user_id: int,
        channel_input: str,
        analysis_result: Dict
    ):
        """Сохранить результат анализа канала в БД"""
        try:
            async with get_session() as session:
                # Генерируем краткое резюме
                summary = self._generate_channel_summary(analysis_result)
                
                # Извлекаем рекомендации
                recommendations = self._extract_recommendations(analysis_result)
                
                analysis = Analysis(
                    user_id=user_id,
                    analysis_type=AnalysisType.BEHAVIORAL,  # Используем для каналов
                    input_data={
                        'channel_input': channel_input,
                        'analysis_type': 'channel'
                    },
                    results=analysis_result,
                    summary=summary,
                    recommendations=recommendations,
                    confidence_score=self._calculate_confidence(analysis_result)
                )
                
                session.add(analysis)
                await session.commit()
                
                logger.info(f"Channel analysis saved for user {user_id}")
                
        except Exception as e:
            logger.error(f"Save channel analysis error: {e}")
    
    def _generate_channel_summary(self, analysis_result: Dict) -> str:
        """Генерация краткого резюме анализа канала"""
        try:
            channel_info = analysis_result.get('channel_info', {})
            content_analysis = analysis_result.get('content_analysis', {})
            
            title = channel_info.get('title', 'Канал')
            subscribers = channel_info.get('participants_count', 0)
            
            llm_analysis = content_analysis.get('llm_analysis', {})
            topic = llm_analysis.get('main_topic', 'разное')
            quality = llm_analysis.get('content_quality', 5)
            
            return f"Анализ канала '{title}' ({subscribers:,} подписчиков): {topic}, качество {quality}/10"
            
        except Exception as e:
            logger.error(f"Generate channel summary error: {e}")
            return "Анализ Telegram канала"
    
    def _extract_recommendations(self, analysis_result: Dict) -> list:
        """Извлечение рекомендаций из результата анализа"""
        try:
            content_analysis = analysis_result.get('content_analysis', {})
            llm_analysis = content_analysis.get('llm_analysis', {})
            
            recommendations = llm_analysis.get('recommendations', [])
            
            # Добавляем общие рекомендации на основе метрик
            channel_info = analysis_result.get('channel_info', {})
            subscribers = channel_info.get('participants_count', 0)
            
            if subscribers < 1000:
                recommendations.append("Сосредоточься на создании качественного контента для роста аудитории")
            
            stats = content_analysis.get('statistics', {})
            engagement = stats.get('engagement_stats', {})
            
            if engagement.get('engagement_rate', 0) < 2:
                recommendations.append("Работай над повышением вовлеченности аудитории")
            
            return recommendations[:5]  # Максимум 5 рекомендаций
            
        except Exception as e:
            logger.error(f"Extract recommendations error: {e}")
            return ["Продолжай развивать канал и анализировать результаты"]
    
    def _calculate_confidence(self, analysis_result: Dict) -> float:
        """Вычисление уверенности в результатах анализа"""
        try:
            confidence_factors = []
            
            # Количество проанализированных сообщений
            analyzed_messages = analysis_result.get('analyzed_messages', 0)
            if analyzed_messages > 50:
                confidence_factors.append(0.9)
            elif analyzed_messages > 20:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Наличие LLM анализа
            content_analysis = analysis_result.get('content_analysis', {})
            if content_analysis.get('llm_analysis'):
                confidence_factors.append(0.8)
            
            # Доступность статистики
            if content_analysis.get('statistics'):
                confidence_factors.append(0.7)
            
            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            
        except Exception as e:
            logger.error(f"Calculate confidence error: {e}")
            return 0.5
    
    async def get_channel_analysis_history(self, user_id: int, limit: int = 10) -> list:
        """Получить историю анализов каналов пользователя"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, desc
                
                result = await session.execute(
                    select(Analysis)
                    .where(
                        Analysis.user_id == user_id,
                        Analysis.analysis_type == AnalysisType.BEHAVIORAL
                    )
                    .order_by(desc(Analysis.created_at))
                    .limit(limit)
                )
                
                analyses = result.scalars().all()
                
                return [
                    {
                        'id': analysis.id,
                        'channel_input': analysis.input_data.get('channel_input', ''),
                        'summary': analysis.summary,
                        'created_at': analysis.created_at.isoformat(),
                        'confidence_score': analysis.confidence_score
                    }
                    for analysis in analyses
                    if analysis.input_data.get('analysis_type') == 'channel'
                ]
                
        except Exception as e:
            logger.error(f"Get channel analysis history error: {e}")
            return []
    
    async def close(self):
        """Закрытие сервиса"""
        if self.channel_analyzer:
            await self.channel_analyzer.close()
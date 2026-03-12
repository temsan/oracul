"""
Анализатор каналов и групп для Oracul Bot
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import openai
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User as TelethonUser
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError

from config.settings import settings

logger = logging.getLogger(__name__)


class ChannelAnalyzer:
    """Анализатор Telegram каналов и групп"""
    
    def __init__(self, session_file: str = "oracul.session"):
        self.client = None
        self.session_file = session_file
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def initialize_client(self, api_id: int, api_hash: str, phone: str = None):
        """Инициализация Telethon клиента"""
        try:
            self.client = TelegramClient(self.session_file, api_id, api_hash)
            await self.client.start(phone=phone)
            logger.info("Telethon client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Telethon client: {e}")
            return False
    
    async def analyze_channel(self, channel_username: str, message_limit: int = 100) -> Dict:
        """
        Анализ канала или группы
        
        Args:
            channel_username: Username канала (@channel_name или ссылка)
            message_limit: Количество сообщений для анализа
            
        Returns:
            Dict с результатами анализа
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Telethon client not initialized'
            }
        
        try:
            # Очищаем username
            clean_username = channel_username.replace('@', '').replace('https://t.me/', '')
            
            # Получаем информацию о канале
            entity = await self.client.get_entity(clean_username)
            
            # Собираем базовую информацию
            channel_info = await self._get_channel_info(entity)
            
            # Собираем сообщения
            messages = await self._collect_messages(entity, message_limit)
            
            if not messages:
                return {
                    'success': False,
                    'error': 'No messages found or access denied'
                }
            
            # Анализируем контент
            content_analysis = await self._analyze_content(messages)
            
            # Анализируем аудиторию (если доступно)
            audience_analysis = await self._analyze_audience(entity)
            
            # Генерируем инсайты
            insights = await self._generate_channel_insights(
                channel_info, content_analysis, audience_analysis
            )
            
            return {
                'success': True,
                'channel_info': channel_info,
                'content_analysis': content_analysis,
                'audience_analysis': audience_analysis,
                'insights': insights,
                'analyzed_messages': len(messages),
                'analysis_date': datetime.now().isoformat()
            }
            
        except ChannelPrivateError:
            return {
                'success': False,
                'error': 'Канал приватный или недоступен'
            }
        except ChatAdminRequiredError:
            return {
                'success': False,
                'error': 'Требуются права администратора для анализа'
            }
        except Exception as e:
            logger.error(f"Channel analysis error: {e}")
            return {
                'success': False,
                'error': f'Ошибка анализа: {str(e)}'
            }
    
    async def _get_channel_info(self, entity) -> Dict:
        """Получение информации о канале"""
        info = {
            'id': entity.id,
            'title': getattr(entity, 'title', 'Unknown'),
            'username': getattr(entity, 'username', None),
            'type': 'channel' if isinstance(entity, Channel) else 'group',
            'participants_count': getattr(entity, 'participants_count', 0),
            'description': getattr(entity, 'about', ''),
            'created_date': getattr(entity, 'date', None),
            'verified': getattr(entity, 'verified', False),
            'scam': getattr(entity, 'scam', False)
        }
        
        # Дополнительная информация для каналов
        if isinstance(entity, Channel):
            info.update({
                'broadcast': entity.broadcast,
                'megagroup': entity.megagroup,
                'signatures': getattr(entity, 'signatures', False)
            })
        
        return info
    
    async def _collect_messages(self, entity, limit: int) -> List[Dict]:
        """Сбор сообщений из канала"""
        messages = []
        
        try:
            async for message in self.client.iter_messages(entity, limit=limit):
                if message.text:  # Только текстовые сообщения
                    msg_data = {
                        'id': message.id,
                        'text': message.text,
                        'date': message.date,
                        'views': getattr(message, 'views', 0),
                        'forwards': getattr(message, 'forwards', 0),
                        'replies': getattr(message.replies, 'replies', 0) if message.replies else 0,
                        'reactions': self._extract_reactions(message),
                        'media_type': 'text'
                    }
                    
                    # Проверяем наличие медиа
                    if message.media:
                        if message.photo:
                            msg_data['media_type'] = 'photo'
                        elif message.video:
                            msg_data['media_type'] = 'video'
                        elif message.document:
                            msg_data['media_type'] = 'document'
                    
                    messages.append(msg_data)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error collecting messages: {e}")
            return []
    
    def _extract_reactions(self, message) -> Dict:
        """Извлечение реакций из сообщения"""
        reactions = {}
        
        if hasattr(message, 'reactions') and message.reactions:
            for reaction in message.reactions.results:
                emoji = reaction.reaction.emoticon if hasattr(reaction.reaction, 'emoticon') else str(reaction.reaction)
                reactions[emoji] = reaction.count
        
        return reactions
    
    async def _analyze_content(self, messages: List[Dict]) -> Dict:
        """Анализ контента сообщений"""
        if not messages:
            return {}
        
        # Объединяем все тексты
        all_text = ' '.join([msg['text'] for msg in messages if msg['text']])
        
        # Базовая статистика
        stats = {
            'total_messages': len(messages),
            'total_characters': len(all_text),
            'total_words': len(all_text.split()),
            'avg_message_length': len(all_text) / len(messages) if messages else 0,
            'media_distribution': self._analyze_media_distribution(messages),
            'engagement_stats': self._analyze_engagement(messages)
        }
        
        # LLM анализ контента
        llm_analysis = await self._analyze_content_with_llm(all_text[:8000])  # Ограничиваем размер
        
        # Анализ тем и ключевых слов
        topics_analysis = self._analyze_topics(all_text)
        
        return {
            'statistics': stats,
            'llm_analysis': llm_analysis,
            'topics': topics_analysis
        }
    
    def _analyze_media_distribution(self, messages: List[Dict]) -> Dict:
        """Анализ распределения типов медиа"""
        media_count = {}
        for msg in messages:
            media_type = msg.get('media_type', 'text')
            media_count[media_type] = media_count.get(media_type, 0) + 1
        
        total = len(messages)
        return {
            media_type: {
                'count': count,
                'percentage': (count / total) * 100 if total > 0 else 0
            }
            for media_type, count in media_count.items()
        }
    
    def _analyze_engagement(self, messages: List[Dict]) -> Dict:
        """Анализ вовлеченности"""
        total_views = sum(msg.get('views', 0) for msg in messages)
        total_forwards = sum(msg.get('forwards', 0) for msg in messages)
        total_replies = sum(msg.get('replies', 0) for msg in messages)
        
        avg_views = total_views / len(messages) if messages else 0
        avg_forwards = total_forwards / len(messages) if messages else 0
        avg_replies = total_replies / len(messages) if messages else 0
        
        return {
            'total_views': total_views,
            'total_forwards': total_forwards,
            'total_replies': total_replies,
            'avg_views': avg_views,
            'avg_forwards': avg_forwards,
            'avg_replies': avg_replies,
            'engagement_rate': (total_forwards + total_replies) / total_views * 100 if total_views > 0 else 0
        }
    
    def _analyze_topics(self, text: str) -> Dict:
        """Простой анализ тем и ключевых слов"""
        words = text.lower().split()
        
        # Ключевые слова по категориям
        business_keywords = ['бизнес', 'стартап', 'деньги', 'инвестиции', 'продажи', 'маркетинг']
        tech_keywords = ['технологии', 'ai', 'ии', 'программирование', 'разработка', 'код']
        career_keywords = ['карьера', 'работа', 'резюме', 'собеседование', 'навыки']
        personal_keywords = ['развитие', 'мотивация', 'цели', 'успех', 'личность']
        
        categories = {
            'business': sum(words.count(word) for word in business_keywords),
            'technology': sum(words.count(word) for word in tech_keywords),
            'career': sum(words.count(word) for word in career_keywords),
            'personal_development': sum(words.count(word) for word in personal_keywords)
        }
        
        # Топ слова
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Только длинные слова
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'categories': categories,
            'top_words': top_words
        }
    
    async def _analyze_content_with_llm(self, text: str) -> Dict:
        """LLM анализ контента канала"""
        if not text or len(text) < 100:
            return {}
        
        try:
            prompt = f"""
Проанализируй контент Telegram канала и дай характеристику:

Текст сообщений: "{text[:4000]}"

Проанализируй:
1. Основную тематику канала
2. Целевую аудиторию
3. Стиль подачи контента
4. Качество контента (1-10)
5. Потенциал монетизации
6. Рекомендации по улучшению

Ответь в формате JSON:
{{
    "main_topic": "основная тематика",
    "target_audience": "описание целевой аудитории",
    "content_style": "стиль подачи",
    "content_quality": 8,
    "monetization_potential": "высокий/средний/низкий",
    "recommendations": ["рекомендация1", "рекомендация2", "рекомендация3"],
    "channel_category": "бизнес/технологии/образование/развлечения/другое"
}}
            """
            
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты эксперт по анализу контента и аудитории Telegram каналов."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"LLM content analysis error: {e}")
            return {}
    
    async def _analyze_audience(self, entity) -> Dict:
        """Анализ аудитории (базовый)"""
        try:
            # Для каналов можем получить только базовую информацию
            audience_info = {
                'total_subscribers': getattr(entity, 'participants_count', 0),
                'channel_type': 'public' if getattr(entity, 'username', None) else 'private',
                'verified': getattr(entity, 'verified', False)
            }
            
            # Для групп можем попробовать получить больше информации
            if hasattr(entity, 'megagroup') and entity.megagroup:
                try:
                    participants = await self.client.get_participants(entity, limit=100)
                    
                    # Анализ активности участников
                    active_users = len([p for p in participants if hasattr(p, 'status') and 
                                      p.status and not getattr(p.status, 'was_online', None)])
                    
                    audience_info.update({
                        'sample_size': len(participants),
                        'active_users_sample': active_users,
                        'activity_rate': (active_users / len(participants)) * 100 if participants else 0
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not analyze audience details: {e}")
            
            return audience_info
            
        except Exception as e:
            logger.error(f"Audience analysis error: {e}")
            return {}
    
    async def _generate_channel_insights(self, channel_info: Dict, content_analysis: Dict, audience_analysis: Dict) -> Dict:
        """Генерация инсайтов о канале"""
        insights = {
            'channel_assessment': {},
            'growth_potential': {},
            'recommendations': [],
            'competitive_analysis': {}
        }
        
        try:
            # Оценка канала
            subscribers = channel_info.get('participants_count', 0)
            engagement_rate = content_analysis.get('statistics', {}).get('engagement_stats', {}).get('engagement_rate', 0)
            
            if subscribers > 10000:
                insights['channel_assessment']['size'] = 'Крупный канал'
            elif subscribers > 1000:
                insights['channel_assessment']['size'] = 'Средний канал'
            else:
                insights['channel_assessment']['size'] = 'Малый канал'
            
            if engagement_rate > 5:
                insights['channel_assessment']['engagement'] = 'Высокая вовлеченность'
            elif engagement_rate > 2:
                insights['channel_assessment']['engagement'] = 'Средняя вовлеченность'
            else:
                insights['channel_assessment']['engagement'] = 'Низкая вовлеченность'
            
            # Потенциал роста
            llm_analysis = content_analysis.get('llm_analysis', {})
            content_quality = llm_analysis.get('content_quality', 5)
            
            if content_quality >= 8:
                insights['growth_potential']['content'] = 'Высокий потенциал'
            elif content_quality >= 6:
                insights['growth_potential']['content'] = 'Средний потенциал'
            else:
                insights['growth_potential']['content'] = 'Требует улучшения'
            
            # Рекомендации
            recommendations = llm_analysis.get('recommendations', [])
            insights['recommendations'] = recommendations[:5]  # Топ 5 рекомендаций
            
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation error: {e}")
            return insights
    
    async def close(self):
        """Закрытие клиента"""
        if self.client:
            await self.client.disconnect()
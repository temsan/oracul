"""
Сервис для работы с пользователями
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import User, SubscriptionType
from database.connection import cache


class UserService:
    """Сервис управления пользователями"""
    
    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Получить или создать пользователя"""
        
        # Проверяем кеш
        cache_key = f"user:{telegram_id}"
        cached_user_id = await cache.get(cache_key)
        
        if cached_user_id:
            # Получаем из БД по ID
            result = await session.execute(
                select(User).where(User.id == int(cached_user_id))
            )
            user = result.scalar_one_or_none()
            if user:
                # Обновляем активность
                user.last_activity = datetime.now(timezone.utc)
                await session.commit()
                return user
        
        # Ищем в БД
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Создаем нового пользователя
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                subscription_type=SubscriptionType.FREE,
                analyses_used_this_month=0,
                last_analysis_reset=datetime.now(timezone.utc)
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            # Обновляем информацию
            user.username = username or user.username
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.last_activity = datetime.now(timezone.utc)
            await session.commit()
        
        # Кешируем
        await cache.set(cache_key, str(user.id), expire=3600)
        
        return user
    
    @staticmethod
    async def update_subscription(
        session: AsyncSession,
        user_id: int,
        subscription_type: SubscriptionType,
        duration_days: int = 30
    ) -> bool:
        """Обновить подписку пользователя"""
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
        
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                subscription_type=subscription_type,
                subscription_expires_at=expires_at,
                updated_at=datetime.now(timezone.utc)
            )
        )
        await session.commit()
        
        # Очищаем кеш
        result = await session.execute(select(User.telegram_id).where(User.id == user_id))
        telegram_id = result.scalar_one_or_none()
        if telegram_id:
            await cache.delete(f"user:{telegram_id}")
        
        return True
    
    @staticmethod
    async def increment_analysis_count(
        session: AsyncSession,
        user_id: int
    ) -> bool:
        """Увеличить счетчик анализов"""
        
        now = datetime.now(timezone.utc)
        
        # Получаем пользователя
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Проверяем, нужно ли сбросить счетчик
        if user.last_analysis_reset.month != now.month:
            user.analyses_used_this_month = 0
            user.last_analysis_reset = now
        
        # Увеличиваем счетчик
        user.analyses_used_this_month += 1
        user.last_activity = now
        
        await session.commit()
        
        # Очищаем кеш
        await cache.delete(f"user:{user.telegram_id}")
        
        return True
    
    @staticmethod
    async def get_user_stats(session: AsyncSession, user_id: int) -> dict:
        """Получить статистику пользователя"""
        
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {}
        
        # Подсчитываем анализы
        from models.database import Analysis
        analyses_result = await session.execute(
            select(Analysis).where(Analysis.user_id == user_id)
        )
        analyses = analyses_result.scalars().all()
        
        return {
            'subscription_type': user.subscription_type.value,
            'is_premium': user.is_premium,
            'analyses_this_month': user.analyses_used_this_month,
            'total_analyses': len(analyses),
            'can_analyze': user.can_analyze(),
            'member_since': user.created_at.isoformat(),
            'last_activity': user.last_activity.isoformat()
        }
    
    @staticmethod
    async def check_user_limits(session: AsyncSession, user_id: int) -> dict:
        """Проверить лимиты пользователя"""
        
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return {'can_analyze': False, 'reason': 'User not found'}
        
        if not user.can_analyze():
            from config.settings import settings
            return {
                'can_analyze': False,
                'reason': 'Monthly limit exceeded',
                'limit': settings.FREE_ANALYSES_PER_MONTH,
                'used': user.analyses_used_this_month,
                'subscription_type': user.subscription_type.value
            }
        
        return {
            'can_analyze': True,
            'remaining': None if user.is_premium else (
                settings.FREE_ANALYSES_PER_MONTH - user.analyses_used_this_month
            ),
            'subscription_type': user.subscription_type.value
        }
"""
Модели базы данных для Oracul Bot
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, JSON, Float, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

Base = declarative_base()


class SubscriptionType(str, Enum):
    """Типы подписок"""
    FREE = "free"
    PREMIUM = "premium" 
    PRO = "pro"


class AnalysisType(str, Enum):
    """Типы анализа"""
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"
    BEHAVIORAL = "behavioral"
    COMPREHENSIVE = "comprehensive"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # Подписка
    subscription_type = Column(SQLEnum(SubscriptionType), default=SubscriptionType.FREE)
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Лимиты
    analyses_used_this_month = Column(Integer, default=0)
    last_analysis_reset = Column(DateTime(timezone=True), default=func.now())
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Настройки
    language = Column(String(10), default="ru")
    timezone_offset = Column(Integer, default=0)  # В минутах от UTC
    
    # Связи
    analyses: Mapped[List["Analysis"]] = relationship("Analysis", back_populates="user")
    insights: Mapped[List["Insight"]] = relationship("Insight", back_populates="user")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, subscription={self.subscription_type})>"
    
    @property
    def is_premium(self) -> bool:
        """Проверка премиум подписки"""
        if self.subscription_type == SubscriptionType.FREE:
            return False
        
        if self.subscription_expires_at:
            return datetime.now(timezone.utc) < self.subscription_expires_at
        
        return True
    
    def can_analyze(self) -> bool:
        """Проверка возможности анализа"""
        if self.is_premium:
            return True
        
        # Проверяем лимит для бесплатных пользователей
        now = datetime.now(timezone.utc)
        if self.last_analysis_reset and self.last_analysis_reset.month != now.month:
            # Сброс счетчика в новом месяце
            self.analyses_used_this_month = 0
            self.last_analysis_reset = now
        
        from config.settings import settings
        return self.analyses_used_this_month < settings.FREE_ANALYSES_PER_MONTH


class Analysis(Base):
    """Модель анализа"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Тип и данные анализа
    analysis_type = Column(SQLEnum(AnalysisType), nullable=False)
    input_data = Column(JSON)  # Исходные данные для анализа
    
    # Результаты
    results = Column(JSON)  # Структурированные результаты
    summary = Column(Text)  # Краткое резюме
    recommendations = Column(Text)  # Рекомендации
    
    # Метрики
    confidence_score = Column(Float, default=0.0)  # Уверенность в анализе (0-1)
    processing_time = Column(Float)  # Время обработки в секундах
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), default=func.now())
    is_favorite = Column(Boolean, default=False)
    
    # Связи
    user: Mapped["User"] = relationship("User", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, type={self.analysis_type}, user_id={self.user_id})>"


class Insight(Base):
    """Модель инсайтов и рекомендаций"""
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Контент
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))  # career, personality, emotions, etc.
    
    # Приоритет и статус
    priority = Column(Integer, default=1)  # 1-5, где 5 - самый важный
    is_read = Column(Boolean, default=False)
    is_actionable = Column(Boolean, default=True)
    
    # Связанные анализы
    related_analysis_ids = Column(JSON)  # Список ID связанных анализов
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    user: Mapped["User"] = relationship("User", back_populates="insights")
    
    def __repr__(self):
        return f"<Insight(id={self.id}, title='{self.title[:50]}...', user_id={self.user_id})>"


class UserSession(Base):
    """Модель пользовательских сессий"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Данные сессии
    session_data = Column(JSON)  # Временные данные сессии
    current_step = Column(String(100))  # Текущий шаг в диалоге
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, step='{self.current_step}')>"


class Analytics(Base):
    """Модель аналитики использования"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Событие
    event_type = Column(String(100), nullable=False)  # start, analysis, subscription, etc.
    event_data = Column(JSON)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), default=func.now())
    ip_address = Column(String(45))  # IPv4/IPv6
    user_agent = Column(Text)
    
    def __repr__(self):
        return f"<Analytics(event_type='{self.event_type}', user_id={self.user_id})>"
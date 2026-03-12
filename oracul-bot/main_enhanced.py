#!/usr/bin/env python3
"""
Расширенный Oracul Bot с мультимодальным анализом и временной динамикой
Интегрирует все возможности: текст, голос, большие объемы, временной анализ
"""

import asyncio
import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Импортируем анализаторы
from analyzers.enhanced_multimodal_analyzer import EnhancedMultimodalAnalyzer
from services.openrouter_service import OpenRouterService

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedOraculBot:
    """Расширенный Oracul Bot с полным мультимодальным анализом"""
    
    def __init__(self):
        self.client = None
        self.analyzer = None
        self.openrouter = None
        self.session_file = "oracul.session"
        
        # Настройки из .env
        self.bot_token = os.getenv('BOT_TOKEN')
        self.admin_ids = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
        
        # Настройки анализа
        self.target_user_id = int(os.getenv('TARGET_USER_ID', '1637334'))
        self.max_messages = int(os.getenv('MAX_MESSAGES_TO_ANALYZE', '200'))
        self.days_back = int(os.getenv('DAYS_BACK_TO_ANALYZE', '30'))
        
    async def initialize(self):
        """Инициализация бота и всех компонентов"""
        try:
            logger.info("🚀 Инициализация расширенного Oracul Bot...")
            
            # Инициализируем Telegram клиент
            if os.path.exists(self.session_file):
                logger.info("📱 Загружаем сессию Telegram...")
                try:
                    with open(self.session_file, 'r', encoding='utf-8') as f:
                        session_string = f.read().strip()
                except UnicodeDecodeError:
                    with open(self.session_file, 'rb') as f:
                        session_string = f.read().decode('utf-8', errors='ignore').strip()
                
                self.client = TelegramClient(
                    StringSession(session_string),
                    api_id=None,
                    api_hash=None
                )
                await self.client.start()
                logger.info("✅ Telegram клиент подключен")
            else:
                logger.error("❌ Файл сессии не найден!")
                return False
            
            # Инициализируем анализаторы
            logger.info("🧠 Инициализация анализаторов...")
            self.analyzer = EnhancedMultimodalAnalyzer()
            await self.analyzer.initialize()
            
            self.openrouter = OpenRouterService()
            
            logger.info("✅ Расширенный Oracul Bot готов к работе")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def collect_chat_data(self, chat_id: int, max_messages: int = None) -> List[Dict]:
        """Сбор данных из чата с поддержкой голосовых сообщений"""
        try:
            if max_messages is None:
                max_messages = self.max_messages
            
            logger.info(f"📥 Сбор данных из чата {chat_id} (макс. {max_messages} сообщений)")
            
            chat = await self.client.get_entity(chat_id)
            messages = []
            
            async for message in self.client.iter_messages(chat, limit=max_messages):
                msg_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'from_id': getattr(message.from_id, 'user_id', None) if message.from_id else None,
                    'type': 'unknown'
                }
                
                # Текстовые сообщения
                if message.text:
                    msg_data.update({
                        'text': message.text,
                        'type': 'text'
                    })
                    messages.append(msg_data)
                
                # Голосовые сообщения
                elif message.media and hasattr(message.media, 'document'):
                    doc = message.media.document
                    if doc.mime_type in ['audio/ogg', 'audio/mpeg', 'audio/wav']:
                        # Определяем длительность
                        duration = 10  # По умолчанию
                        for attr in doc.attributes:
                            if hasattr(attr, 'duration'):
                                duration = attr.duration
                                break
                        
                        msg_data.update({
                            'type': 'voice',
                            'duration': duration,
                            'voice_file': message  # Сохраняем объект сообщения для скачивания
                        })
                        messages.append(msg_data)
            
            logger.info(f"✅ Собрано {len(messages)} сообщений")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Ошибка сбора данных: {e}")
            return []
    
    async def perform_comprehensive_analysis(self, chat_id: int) -> Dict:
        """Выполнение комплексного анализа чата"""
        try:
            logger.info(f"🔮 Начинаем комплексный анализ чата {chat_id}")
            
            # 1. Сбор данных
            messages = await self.collect_chat_data(chat_id)
            if not messages:
                return {'success': False, 'error': 'No messages collected'}
            
            # 2. Мультимодальный анализ большого объема данных
            logger.info("🧠 Запуск мультимодального анализа...")
            analysis_result = await self.analyzer.analyze_large_dataset(
                messages, 
                max_messages=self.max_messages,
                use_modern=True
            )
            
            if not analysis_result.get('success'):
                return analysis_result
            
            # 3. Временной анализ динамики
            logger.info("⏰ Анализ временной динамики...")
            temporal_result = await self.analyzer.analyze_temporal_dynamics(
                analysis_result['analyses'],
                time_window_hours=24
            )
            
            # 4. Создание итогового отчета
            comprehensive_report = {
                'chat_id': chat_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_collection': {
                    'total_messages_found': len(messages),
                    'messages_processed': analysis_result['total_processed'],
                    'processing_efficiency': f"{analysis_result['total_processed']}/{len(messages)}"
                },
                'multimodal_analysis': analysis_result,
                'temporal_dynamics': temporal_result,
                'comprehensive_insights': self._generate_comprehensive_insights(
                    analysis_result, temporal_result
                )
            }
            
            # 5. Сохранение отчета
            report_file = await self._save_comprehensive_report(comprehensive_report)
            comprehensive_report['report_file'] = report_file
            
            logger.info("✅ Комплексный анализ завершен")
            return {
                'success': True,
                'report': comprehensive_report
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка комплексного анализа: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_comprehensive_insights(self, analysis_result: Dict, temporal_result: Dict) -> List[str]:
        """Генерация комплексных инсайтов"""
        try:
            insights = []
            
            # Инсайты из мультимодального анализа
            overall_summary = analysis_result.get('overall_summary', {})
            
            total_messages = overall_summary.get('total_messages', 0)
            text_messages = overall_summary.get('text_messages', 0)
            voice_messages = overall_summary.get('voice_messages', 0)
            
            insights.append(f"Проанализировано {total_messages} сообщений: {text_messages} текстовых, {voice_messages} голосовых")
            
            # Тональность
            sentiment_dist = overall_summary.get('sentiment_distribution', {})
            if sentiment_dist:
                dominant_sentiment = max(sentiment_dist.items(), key=lambda x: x[1])
                insights.append(f"Доминирующая тональность: {dominant_sentiment[0]} ({dominant_sentiment[1]} сообщений)")
            
            # Временная динамика
            if temporal_result.get('success'):
                dynamics = temporal_result.get('dynamics', {})
                temporal_insights = dynamics.get('insights', [])
                insights.extend(temporal_insights)
                
                # Активность
                activity = dynamics.get('activity_patterns', {})
                avg_messages = activity.get('avg_messages_per_window', 0)
                if avg_messages > 0:
                    insights.append(f"Средняя активность: {avg_messages:.1f} сообщений за 24 часа")
            
            # Эффективность обработки
            batches = analysis_result.get('batches_processed', 0)
            if batches > 0:
                insights.append(f"Обработано {batches} батчей с высокой эффективностью")
            
            return insights
            
        except Exception as e:
            logger.error(f"Ошибка генерации инсайтов: {e}")
            return ["Ошибка генерации комплексных инсайтов"]
    
    async def _save_comprehensive_report(self, report: Dict) -> str:
        """Сохранение комплексного отчета"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chat_id = report.get('chat_id', 'unknown')
            filename = f"analysis/chat_{chat_id}_comprehensive_analysis_{timestamp}.json"
            
            # Создаем директорию
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 Комплексный отчет сохранен: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения отчета: {e}")
            return ""
    
    async def handle_analysis_command(self, chat_id: int, user_id: int) -> str:
        """Обработка команды анализа"""
        try:
            # Проверяем права доступа
            if user_id not in self.admin_ids:
                return "❌ Недостаточно прав для выполнения анализа"
            
            # Выполняем анализ
            result = await self.perform_comprehensive_analysis(chat_id)
            
            if result.get('success'):
                report = result['report']
                insights = report.get('comprehensive_insights', [])
                
                response = "✅ Комплексный анализ завершен!\n\n"
                response += f"📊 Чат ID: {chat_id}\n"
                response += f"📈 Обработано сообщений: {report['data_collection']['messages_processed']}\n"
                response += f"⏰ Временной анализ: {'✅' if report['temporal_dynamics'].get('success') else '❌'}\n\n"
                
                response += "💡 Ключевые инсайты:\n"
                for i, insight in enumerate(insights[:5], 1):
                    response += f"{i}. {insight}\n"
                
                if report.get('report_file'):
                    response += f"\n📄 Полный отчет: {report['report_file']}"
                
                return response
            else:
                return f"❌ Ошибка анализа: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Ошибка обработки команды: {e}")
            return f"❌ Критическая ошибка: {str(e)}"
    
    async def run(self):
        """Запуск бота"""
        try:
            if not await self.initialize():
                logger.error("❌ Не удалось инициализировать бота")
                return
            
            logger.info("🤖 Расширенный Oracul Bot запущен и готов к работе!")
            
            # Пример автоматического анализа целевого пользователя
            if self.target_user_id:
                logger.info(f"🎯 Запуск автоматического анализа пользователя {self.target_user_id}")
                result = await self.perform_comprehensive_analysis(self.target_user_id)
                
                if result.get('success'):
                    logger.info("✅ Автоматический анализ завершен успешно")
                else:
                    logger.error(f"❌ Ошибка автоматического анализа: {result.get('error')}")
            
            # Держим бота активным
            logger.info("🔄 Бот работает в фоновом режиме...")
            while True:
                await asyncio.sleep(60)  # Проверяем каждую минуту
                
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал остановки")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
        finally:
            if self.client:
                await self.client.disconnect()
            logger.info("👋 Расширенный Oracul Bot остановлен")


async def main():
    """Главная функция"""
    bot = EnhancedOraculBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
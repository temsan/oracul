#!/usr/bin/env python3
"""
Упрощенная версия Oracul Bot для быстрого запуска
Использует только базовые зависимости
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.simple_analyzer import SimpleAnalyzer

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleOracul:
    """Упрощенный бот Oracul"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.session_file = "oracul.session"
        self.bot_client = None
        self.user_client = None
        self.analyzer = None
        
        # Проверяем загрузку переменных
        if not self.bot_token:
            logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
            raise ValueError("BOT_TOKEN не настроен")
        
        logger.info(f"✅ BOT_TOKEN загружен: {self.bot_token[:10]}...")
        
        # Состояния пользователей
        self.user_states = {}
    
    async def initialize(self):
        """Инициализация бота"""
        try:
            logger.info("🚀 Инициализация упрощенного Oracul бота...")
            
            # Инициализируем бот клиент
            api_id = os.getenv('TG_API_ID')
            api_hash = os.getenv('TG_API_HASH')
            
            if not api_id or not api_hash:
                logger.error("❌ TG_API_ID или TG_API_HASH не настроены!")
                return False
            
            self.bot_client = TelegramClient('bot_session', api_id, api_hash)
            await self.bot_client.start(bot_token=self.bot_token)
            logger.info("✅ Бот клиент подключен")
            
            # Инициализируем пользовательский клиент для сбора данных
            if os.path.exists(self.session_file):
                logger.info("📱 Загружаем сессию Telegram...")
                
                self.user_client = TelegramClient(
                    self.session_file,
                    api_id=api_id,
                    api_hash=api_hash
                )
                await self.user_client.start()
                logger.info("✅ Пользовательский клиент подключен")
            else:
                logger.warning("⚠️ Файл сессии не найден, пользовательский клиент недоступен")
            
            # Инициализируем анализатор
            self.analyzer = SimpleAnalyzer()
            await self.analyzer.initialize()
            
            logger.info("✅ Упрощенный Oracul бот готов к работе")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def handle_start(self, event):
        """Обработка команды /start"""
        welcome_text = """
🔮 **Добро пожаловать в Simple Oracul Bot!**

Упрощенная версия бота для самоанализа диалогов.

**Возможности:**
💬 Анализ личных чатов
📊 Базовая статистика сообщений
🎯 Определение основных тем
😊 Анализ тональности

**Команды:**
/start - Главное меню
/help - Справка
/analyze - Быстрый анализ

Выберите действие:
"""
        
        buttons = [
            [Button.inline('💬 Анализ чата', b'analyze_chat')],
            [Button.inline('📊 Статистика', b'statistics')],
            [Button.inline('ℹ️ Помощь', b'help')]
        ]
        
        await event.respond(
            welcome_text,
            buttons=buttons,
            parse_mode='markdown'
        )
    
    async def handle_analyze_chat(self, event):
        """Обработка анализа чата"""
        if not self.user_client:
            await event.edit(
                "❌ **Пользовательский клиент недоступен**\n\n"
                "Для анализа чатов нужен файл сессии oracul.session\n"
                "Обратитесь к администратору для настройки.",
                buttons=[[Button.inline('◀️ Назад', b'back_to_main')]],
                parse_mode='markdown'
            )
            return
        
        await event.edit(
            "💬 **Анализ чата**\n\n"
            "Отправьте ID чата для анализа или выберите из списка.\n\n"
            "Пример: -1001234567890",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'back_to_main')]
            ],
            parse_mode='markdown'
        )
        
        user_id = event.sender_id
        self.user_states[user_id] = {'state': 'waiting_chat_id'}
    
    async def handle_show_chats(self, event):
        """Показать список чатов"""
        try:
            await event.edit("🔄 Загружаю ваши чаты...")
            
            chats = []
            async for dialog in self.user_client.iter_dialogs(limit=20):
                if dialog.is_user and not getattr(dialog.entity, 'bot', False):
                    chats.append({
                        'id': dialog.id,
                        'name': dialog.name[:20],
                        'unread': dialog.unread_count
                    })
            
            if not chats:
                await event.edit(
                    "❌ **Личные чаты не найдены**\n\n"
                    "Возможные причины:\n"
                    "• Нет активных личных чатов\n"
                    "• Ограничения доступа к диалогам",
                    buttons=[[Button.inline('◀️ Назад', b'analyze_chat')]],
                    parse_mode='markdown'
                )
                return
            
            buttons = []
            for chat in chats[:10]:
                chat_name = chat['name']
                if chat['unread'] > 0:
                    chat_name += f" ({chat['unread']})"
                
                buttons.append([Button.inline(
                    f"💬 {chat_name}", 
                    f"chat_{chat['id']}".encode()
                )])
            
            buttons.append([Button.inline('◀️ Назад', b'analyze_chat')])
            
            await event.edit(
                f"💬 **Ваши личные чаты** ({len(chats)})\n\n"
                f"Показано: {min(10, len(chats))} из {len(chats)}\n\n"
                "Выберите чат для анализа:",
                buttons=buttons,
                parse_mode='markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения списка чатов: {e}")
            await event.edit(f"❌ Ошибка: {str(e)}")
    
    async def handle_chat_selection(self, event, chat_id: int):
        """Обработка выбора чата"""
        try:
            chat = await self.user_client.get_entity(chat_id)
            chat_name = getattr(chat, 'first_name', f'Чат {chat_id}')
        except:
            chat_name = f"Чат {chat_id}"
        
        await event.edit(
            f"🔄 Анализирую чат **{chat_name}**\n\n"
            f"⏳ Собираю сообщения...",
            parse_mode='markdown'
        )
        
        try:
            # Собираем сообщения
            messages = await self.collect_chat_messages(chat_id, limit=50)
            
            if not messages:
                await event.edit(
                    f"❌ В чате **{chat_name}** не найдено сообщений для анализа",
                    buttons=[[Button.inline('◀️ Назад', b'show_chats')]],
                    parse_mode='markdown'
                )
                return
            
            await event.edit(
                f"🔄 Анализирую {len(messages)} сообщений из чата **{chat_name}**\n\n"
                f"⏳ Это займет несколько секунд...",
                parse_mode='markdown'
            )
            
            # Выполняем анализ
            result = await self.analyzer.create_combined_analysis(messages)
            
            if result.get('success'):
                await self.send_analysis_result(event, result, chat_name)
            else:
                await event.edit(f"❌ Ошибка анализа: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Ошибка анализа чата: {e}")
            await event.edit(f"❌ Критическая ошибка: {str(e)}")
    
    async def collect_chat_messages(self, chat_id: int, limit: int = 50) -> List[Dict]:
        """Сбор сообщений из чата"""
        try:
            messages = []
            chat = await self.user_client.get_entity(chat_id)
            
            async for message in self.user_client.iter_messages(chat, limit=limit):
                if message.text:
                    messages.append({
                        'id': message.id,
                        'date': message.date.isoformat(),
                        'text': message.text,
                        'type': 'text'
                    })
                elif message.media and hasattr(message.media, 'document'):
                    doc = message.media.document
                    if doc.mime_type in ['audio/ogg', 'audio/mpeg', 'audio/wav']:
                        messages.append({
                            'id': message.id,
                            'date': message.date.isoformat(),
                            'type': 'voice',
                            'duration': 10  # Примерная длительность
                        })
            
            return messages
            
        except Exception as e:
            logger.error(f"Ошибка сбора сообщений: {e}")
            return []
    
    async def send_analysis_result(self, event, result: Dict, chat_name: str):
        """Отправка результата анализа"""
        try:
            stats = result.get('statistics', {})
            summary = result.get('dialog_summary', {}).get('summary', {})
            
            response = f"✅ **Анализ чата: {chat_name}**\n\n"
            response += f"📊 **Статистика:**\n"
            response += f"• Всего сообщений: {stats.get('total_messages', 0)}\n"
            response += f"• Текстовых: {stats.get('text_messages', 0)}\n"
            response += f"• Голосовых: {stats.get('voice_messages', 0)}\n"
            response += f"• Слов: {stats.get('word_count', 0)}\n\n"
            
            # Основные темы
            main_topics = summary.get('main_topics', [])
            if main_topics:
                response += f"📌 **Основные темы:**\n"
                for topic in main_topics[:5]:
                    response += f"  • {topic}\n"
                response += "\n"
            
            # Тональность
            tone = summary.get('overall_tone', 'неизвестная')
            response += f"😊 **Тональность:** {tone}\n\n"
            
            # Краткое саммари
            summary_text = summary.get('summary_text', '')
            if summary_text:
                response += f"📝 **Краткое саммари:**\n{summary_text}\n\n"
            
            response += f"⏰ Анализ выполнен: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            buttons = [
                [
                    Button.inline('🔄 Новый анализ', b'analyze_chat'),
                    Button.inline('📋 Другой чат', b'show_chats')
                ],
                [Button.inline('🏠 Главное меню', b'back_to_main')]
            ]
            
            await event.edit(response, buttons=buttons, parse_mode='markdown')
            
        except Exception as e:
            logger.error(f"Ошибка отправки результата: {e}")
            await event.edit(f"✅ Анализ завершен, но возникла ошибка форматирования: {str(e)}")
    
    async def handle_message(self, event):
        """Обработка текстовых сообщений"""
        user_id = event.sender_id
        user_state = self.user_states.get(user_id, {})
        
        if user_state.get('state') == 'waiting_chat_id':
            try:
                chat_id = int(event.text.strip())
                await self.handle_chat_selection(event, chat_id)
                # Очищаем состояние
                if user_id in self.user_states:
                    del self.user_states[user_id]
            except ValueError:
                await event.respond("❌ Неверный формат ID чата. Введите числовой ID.")
    
    async def run(self):
        """Запуск бота"""
        try:
            if not await self.initialize():
                logger.error("❌ Не удалось инициализировать бота")
                return
            
            # Обработчики команд
            @self.bot_client.on(events.NewMessage(pattern='/start'))
            async def start_handler(event):
                await self.handle_start(event)
            
            @self.bot_client.on(events.NewMessage(pattern='/help'))
            async def help_handler(event):
                help_text = """
ℹ️ **Simple Oracul Bot - Справка**

**Команды:**
/start - Главное меню
/help - Эта справка
/analyze - Быстрый анализ

**Возможности:**
💬 Анализ личных чатов
📊 Статистика сообщений
🎯 Определение тем
😊 Анализ тональности

**Как использовать:**
1. Нажмите "Анализ чата"
2. Выберите чат из списка или введите ID
3. Получите результат анализа

**Поддержка:**
Если возникли проблемы, обратитесь к администратору.
"""
                await event.respond(help_text, parse_mode='markdown')
            
            @self.bot_client.on(events.NewMessage(pattern='/analyze'))
            async def analyze_handler(event):
                await self.handle_analyze_chat(event)
            
            # Обработчик текстовых сообщений
            @self.bot_client.on(events.NewMessage)
            async def message_handler(event):
                if not event.text.startswith('/'):
                    await self.handle_message(event)
            
            # Обработчики кнопок
            @self.bot_client.on(events.CallbackQuery)
            async def callback_handler(event):
                data = event.data.decode()
                
                if data == 'analyze_chat':
                    await self.handle_analyze_chat(event)
                elif data == 'show_chats':
                    await self.handle_show_chats(event)
                elif data.startswith('chat_'):
                    chat_id = int(data.split('_', 1)[1])
                    await self.handle_chat_selection(event, chat_id)
                elif data == 'back_to_main':
                    await self.handle_start(event)
                elif data == 'help':
                    await event.edit(
                        "ℹ️ **Справка**\n\n"
                        "Используйте кнопки меню для навигации.\n"
                        "Для анализа чата выберите 'Анализ чата'.",
                        buttons=[[Button.inline('◀️ Назад', b'back_to_main')]],
                        parse_mode='markdown'
                    )
                elif data == 'statistics':
                    await event.edit(
                        "📊 **Статистика**\n\n"
                        "Функция в разработке.\n"
                        "Скоро будет доступна!",
                        buttons=[[Button.inline('◀️ Назад', b'back_to_main')]],
                        parse_mode='markdown'
                    )
                else:
                    await event.answer("⚠️ Функция в разработке")
            
            logger.info("🤖 Simple Oracul бот запущен и готов к работе!")
            logger.info("📱 Отправьте /start боту для начала работы")
            
            # Держим бота активным
            await self.bot_client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал остановки")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.bot_client:
                await self.bot_client.disconnect()
            if self.user_client:
                await self.user_client.disconnect()
            logger.info("👋 Бот остановлен")


async def main():
    """Главная функция"""
    bot = SimpleOracul()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
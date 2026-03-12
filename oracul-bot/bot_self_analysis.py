#!/usr/bin/env python3
"""
Telegram бот для самоанализа диалогов по темам
Интерфейс для анализа личных чатов пользователя
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.dialog_summary_analyzer_simple import DialogSummaryAnalyzer

# Загружаем переменные окружения
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
print(f"🔧 Загружаем .env из: {env_path}")
print(f"🔧 BOT_TOKEN найден: {'✅' if os.getenv('BOT_TOKEN') else '❌'}")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SelfAnalysisBot:
    """Бот для самоанализа диалогов"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.session_file = "oracul.session"
        self.bot_client = None
        self.user_client = None
        self.analyzer = None
        
        # Проверяем загрузку переменных
        if not self.bot_token:
            logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
            logger.error(f"Текущая директория: {os.getcwd()}")
            logger.error(f"Путь к .env: {Path(__file__).parent.parent / '.env'}")
            raise ValueError("BOT_TOKEN не настроен")
        
        logger.info(f"✅ BOT_TOKEN загружен: {self.bot_token[:10]}...")
        
        # Состояния пользователей
        self.user_states = {}
        
        # Темы для анализа
        self.analysis_topics = {
            '1': {'name': '💼 Работа и карьера', 'keywords': ['работа', 'проект', 'задача', 'встреча', 'дедлайн']},
            '2': {'name': '👥 Отношения', 'keywords': ['друг', 'семья', 'отношения', 'любовь', 'встреча']},
            '3': {'name': '🎯 Цели и планы', 'keywords': ['цель', 'план', 'хочу', 'буду', 'планирую']},
            '4': {'name': '😊 Эмоции и настроение', 'keywords': ['чувствую', 'настроение', 'эмоции', 'переживаю']},
            '5': {'name': '🧠 Саморазвитие', 'keywords': ['учу', 'изучаю', 'развитие', 'навык', 'книга']},
            '6': {'name': '💭 Общий анализ', 'keywords': []}  # Без фильтрации
        }
    
    async def initialize(self):
        """Инициализация бота"""
        try:
            logger.info("🚀 Инициализация бота самоанализа...")
            
            # Инициализируем бот клиент
            api_id = os.getenv('TG_API_ID')
            api_hash = os.getenv('TG_API_HASH')
            
            # Проверяем, что API данные настроены
            if not api_id or api_id == 'YOUR_API_ID_HERE':
                logger.error("❌ TG_API_ID не настроен!")
                return False
            
            if not api_hash or api_hash == 'YOUR_API_HASH_HERE':
                logger.error("❌ TG_API_HASH не настроен!")
                return False
            
            try:
                api_id = int(api_id)
            except ValueError:
                logger.error("❌ TG_API_ID должен быть числом!")
                return False
            
            self.bot_client = TelegramClient('bot_session', api_id, api_hash)
            await self.bot_client.start(bot_token=self.bot_token)
            logger.info("✅ Бот клиент подключен")
            
            # Инициализируем пользовательский клиент для сбора данных
            if os.path.exists(self.session_file):
                logger.info("📱 Загружаем сессию Telegram...")
                
                # Используем файл сессии напрямую
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
            self.analyzer = DialogSummaryAnalyzer()
            await self.analyzer.initialize()
            
            logger.info("✅ Бот самоанализа готов к работе")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    def get_main_menu(self):
        """Главное меню с расширенными кнопками"""
        buttons = [
            [Button.inline('📊 Анализ по темам', b'topics')],
            [Button.inline('💬 Выбрать чат для анализа', b'select_chat')],
            [
                Button.inline('🔍 Быстрый анализ', b'quick_analysis'),
                Button.inline('📈 Глубокий анализ', b'deep_analysis')
            ],
            [
                Button.inline('🎤 Только голосовые', b'voice_only'),
                Button.inline('📝 Только текст', b'text_only')
            ],
            [
                Button.inline('🌍 Глобальный анализ', b'global_analysis')
            ],
            [
                Button.inline('📅 За последний месяц', b'last_month'),
                Button.inline('📆 За последнюю неделю', b'last_week')
            ],
            [Button.inline('📈 История анализов', b'history')],
            [Button.inline('ℹ️ Помощь', b'help')]
        ]
        return buttons
    
    def get_topics_menu(self):
        """Меню выбора темы с дополнительными опциями"""
        buttons = []
        for topic_id, topic_data in self.analysis_topics.items():
            buttons.append([Button.inline(topic_data['name'], f'topic_{topic_id}'.encode())])
        
        # Дополнительные опции анализа
        buttons.extend([
            [
                Button.inline('🔥 Популярные темы', b'popular_topics'),
                Button.inline('🎯 Персональные инсайты', b'personal_insights')
            ],
            [Button.inline('◀️ Назад', b'back')]
        ])
        return buttons
    
    async def handle_start(self, event):
        """Обработка команды /start"""
        user_id = event.sender_id
        
        welcome_text = """
🔮 **Добро пожаловать в Oracul Self-Analysis Bot!**

Я помогу вам проанализировать ваши диалоги и получить инсайты о:
• Темах, которые вас волнуют
• Эмоциональных паттернах
• Динамике общения
• Ключевых моментах диалогов

**Что я умею:**
📊 Анализ диалогов по темам
💬 Саммари любого чата
🎤 Анализ голосовых сообщений
📈 Временная динамика общения

Выберите действие:
"""
        
        await event.respond(
            welcome_text,
            buttons=self.get_main_menu(),
            parse_mode='markdown'
        )
    
    async def handle_topics(self, event):
        """Обработка выбора анализа по темам"""
        await event.edit(
            "📊 **Выберите тему для анализа:**\n\n"
            "Я проанализирую ваши диалоги и найду сообщения, "
            "связанные с выбранной темой.",
            buttons=self.get_topics_menu(),
            parse_mode='markdown'
        )
    
    async def handle_topic_selection(self, event, topic_id):
        """Обработка выбора конкретной темы"""
        user_id = event.sender_id
        topic_data = self.analysis_topics.get(topic_id)
        
        if not topic_data:
            await event.answer("❌ Тема не найдена")
            return
        
        # Сохраняем выбранную тему
        self.user_states[user_id] = {
            'state': 'waiting_chat',
            'topic_id': topic_id,
            'topic_name': topic_data['name']
        }
        
        await event.edit(
            f"✅ Выбрана тема: **{topic_data['name']}**\n\n"
            f"Теперь отправьте мне ID чата для анализа или используйте /chats для просмотра списка.",
            buttons=[[Button.inline('◀️ Назад к темам', b'topics')]],
            parse_mode='markdown'
        )
    
    async def handle_select_chat(self, event):
        """Обработка выбора чата"""
        user_id = event.sender_id
        
        await event.edit(
            "💬 **Выбор чата для анализа**\n\n"
            "Используйте команду /chats чтобы увидеть список ваших чатов.\n\n"
            "Или отправьте ID чата напрямую (например: 1637334)",
            buttons=[[Button.inline('◀️ Назад', b'back')]],
            parse_mode='markdown'
        )
    
    async def handle_chats_list(self, event):
        """Показать список чатов пользователя"""
        try:
            await event.respond("🔄 Загружаю список ваших чатов...")
            
            # Получаем список диалогов
            dialogs = []
            async for dialog in self.user_client.iter_dialogs(limit=50):
                if dialog.is_user:  # Только личные чаты
                    entity = dialog.entity
                    
                    # Фильтруем ботов
                    if hasattr(entity, 'bot') and entity.bot:
                        continue  # Пропускаем ботов
                    
                    # Фильтруем по username (если есть username с bot)
                    if hasattr(entity, 'username') and entity.username:
                        if 'bot' in entity.username.lower():
                            continue  # Пропускаем ботов по username
                    
                    dialogs.append({
                        'id': dialog.id,
                        'name': dialog.name,
                        'unread': dialog.unread_count,
                        'username': getattr(entity, 'username', None)
                    })
            
            if not dialogs:
                await event.respond(
                    "❌ **Личные чаты не найдены**\n\n"
                    "Возможные причины:\n"
                    "• Все диалоги с ботами (исключены из списка)\n"
                    "• Нет активных личных чатов\n"
                    "• Ограничения доступа к диалогам\n\n"
                    "💡 Попробуйте использовать кнопку 'Выбрать чат' в главном меню"
                )
                return
            
            # Формируем список
            chat_list = f"💬 **Ваши личные чаты** ({len(dialogs)}):\n\n"
            chat_list += "🤖 *Боты исключены из списка*\n\n"
            
            for i, dialog in enumerate(dialogs[:15], 1):  # Показываем до 15 чатов
                chat_list += f"{i}. **{dialog['name']}**\n"
                chat_list += f"   ID: `{dialog['id']}`\n"
                
                if dialog.get('username'):
                    chat_list += f"   👤 @{dialog['username']}\n"
                
                if dialog['unread'] > 0:
                    chat_list += f"   📬 Непрочитанных: {dialog['unread']}\n"
                chat_list += "\n"
            
            if len(dialogs) > 15:
                chat_list += f"... и еще {len(dialogs) - 15} чатов\n\n"
            
            chat_list += "📝 Отправьте ID чата для анализа"
            
            await event.respond(chat_list, parse_mode='markdown')
            
        except Exception as e:
            logger.error(f"Ошибка получения списка чатов: {e}")
            await event.respond(f"❌ Ошибка: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def handle_chat_id(self, event):
        """Обработка ID чата для анализа"""
        user_id = event.sender_id
        text = event.text.strip()
        
        # Проверяем, что это число
        try:
            chat_id = int(text)
        except ValueError:
            return  # Не ID чата
        
        # Проверяем состояние пользователя
        user_state = self.user_states.get(user_id, {})
        topic_id = user_state.get('topic_id', '6')  # По умолчанию общий анализ
        topic_name = user_state.get('topic_name', '💭 Общий анализ')
        
        await event.respond(
            f"🔄 Начинаю анализ чата {chat_id}\n"
            f"📊 Тема: {topic_name}\n\n"
            f"⏳ Это может занять некоторое время..."
        )
        
        # Запускаем анализ
        try:
            result = await self.analyze_chat(chat_id, topic_id)
            
            if result.get('success'):
                await self.send_analysis_result(event, result)
            else:
                await event.respond(f"❌ Ошибка анализа: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Ошибка анализа чата: {e}")
            await event.respond(f"❌ Критическая ошибка: {str(e)}")
        
        # Очищаем состояние
        if user_id in self.user_states:
            del self.user_states[user_id]
    
    async def analyze_chat(self, chat_id: int, topic_id: str) -> dict:
        """Анализ чата по теме"""
        try:
            logger.info(f"📊 Анализ чата {chat_id}, тема: {topic_id}")
            
            # Собираем сообщения из чата
            messages = await self.collect_chat_messages(chat_id, limit=200)
            
            if not messages:
                return {'success': False, 'error': 'Не найдено сообщений в чате'}
            
            # Фильтруем по теме (если не общий анализ)
            topic_data = self.analysis_topics.get(topic_id, {})
            keywords = topic_data.get('keywords', [])
            
            if keywords:
                filtered_messages = self.filter_by_keywords(messages, keywords)
                logger.info(f"Отфильтровано {len(filtered_messages)} из {len(messages)} сообщений")
            else:
                filtered_messages = messages
            
            if not filtered_messages:
                return {
                    'success': False, 
                    'error': f'Не найдено сообщений по теме "{topic_data.get("name")}"'
                }
            
            # Анализируем
            result = await self.analyzer.create_combined_analysis(
                filtered_messages,
                participant_names=['Вы', 'Собеседник']
            )
            
            if result.get('success'):
                result['topic_name'] = topic_data.get('name', 'Общий анализ')
                result['total_messages_in_chat'] = len(messages)
                result['filtered_messages'] = len(filtered_messages)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка анализа: {e}")
            return {'success': False, 'error': str(e)}
    
    async def collect_chat_messages(self, chat_id: int, limit: int = 200) -> list:
        """Сбор сообщений из любого типа чата"""
        try:
            messages = []
            chat = await self.user_client.get_entity(chat_id)
            
            logger.info(f"📥 Сбор сообщений из чата: {getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))}")
            
            async for message in self.user_client.iter_messages(chat, limit=limit):
                msg_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'from_id': getattr(message.from_id, 'user_id', None) if message.from_id else None,
                    'chat_type': 'group' if hasattr(chat, 'participants_count') else 'personal'
                }
                
                # Для групповых чатов добавляем информацию об отправителе
                if hasattr(chat, 'participants_count'):
                    try:
                        sender = await message.get_sender()
                        if sender:
                            msg_data['sender_name'] = getattr(sender, 'first_name', 'Unknown')
                    except:
                        msg_data['sender_name'] = 'Unknown'
                
                if message.text:
                    msg_data['text'] = message.text
                    msg_data['type'] = 'text'
                    messages.append(msg_data)
                elif message.media and hasattr(message.media, 'document'):
                    doc = message.media.document
                    if doc.mime_type in ['audio/ogg', 'audio/mpeg', 'audio/wav']:
                        duration = 10
                        for attr in doc.attributes:
                            if hasattr(attr, 'duration'):
                                duration = attr.duration
                                break
                        
                        msg_data['type'] = 'voice'
                        msg_data['duration'] = duration
                        msg_data['voice_file'] = message
                        messages.append(msg_data)
            
            logger.info(f"✅ Собрано {len(messages)} сообщений")
            return messages
            
        except Exception as e:
            logger.error(f"Ошибка сбора сообщений: {e}")
            return []
    
    def filter_by_keywords(self, messages: list, keywords: list) -> list:
        """Фильтрация сообщений по ключевым словам"""
        filtered = []
        
        for msg in messages:
            text = msg.get('text', '').lower()
            if any(keyword.lower() in text for keyword in keywords):
                filtered.append(msg)
        
        return filtered
    
    async def send_analysis_result(self, event, result: dict):
        """Отправка результата анализа"""
        try:
            analysis_type_name = result.get('analysis_type_name', 'Анализ')
            stats = result.get('statistics', {})
            
            # Основная информация
            response = f"✅ **{analysis_type_name}**\n\n"
            response += f"📊 **Статистика:**\n"
            response += f"• Всего сообщений в чате: {result.get('total_messages_in_chat', 0)}\n"
            response += f"• Проанализировано: {result.get('filtered_messages', 0)}\n"
            response += f"• Текстовых: {stats.get('text_messages', 0)}\n"
            response += f"• Голосовых: {stats.get('voice_messages', 0)}\n"
            
            # Тип чата
            chat_type = result.get('chat_type', 'unknown')
            if chat_type == 'group':
                response += f"• Тип чата: 👥 Групповой\n"
            else:
                response += f"• Тип чата: 👤 Личный\n"
            
            response += "\n"
            
            # Саммари диалога
            dialog_summary = result.get('dialog_summary', {})
            if dialog_summary:
                summary_data = dialog_summary.get('summary', {})
                
                if isinstance(summary_data, dict):
                    response += "💡 **Ключевые инсайты:**\n"
                    
                    # Основные темы
                    main_topics = summary_data.get('main_topics', [])
                    if main_topics:
                        response += "\n📌 Основные темы:\n"
                        for topic in main_topics[:3]:
                            response += f"  • {topic}\n"
                    
                    # Тональность
                    overall_tone = summary_data.get('overall_tone')
                    if overall_tone:
                        response += f"\n😊 Общая тональность: {overall_tone}\n"
                    
                    # Краткое саммари
                    summary_text = summary_data.get('summary_text')
                    if summary_text:
                        response += f"\n📝 **Краткое саммари:**\n{summary_text}\n"
            
            # Общие инсайты
            insights = result.get('insights', [])
            if insights:
                response += "\n\n🎯 **Общие наблюдения:**\n"
                for insight in insights[:5]:
                    response += f"• {insight}\n"
            
            # Голосовой анализ
            voice_analysis = result.get('voice_analysis', {})
            if voice_analysis:
                voice_summary = voice_analysis.get('summary', {})
                total_duration = voice_summary.get('total_duration_minutes', 0)
                if total_duration > 0:
                    response += f"\n\n🎤 **Голосовые сообщения:**\n"
                    response += f"• Общая длительность: {total_duration:.1f} мин\n"
                    response += f"• Количество: {voice_summary.get('message_count', 0)}\n"
            
            response += f"\n\n⏰ Анализ выполнен: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            # Добавляем кнопки для дополнительных действий
            buttons = [
                [
                    Button.inline('🔄 Новый анализ', b'back'),
                    Button.inline('📋 Другой чат', b'show_chats')
                ]
            ]
            
            await event.respond(response, buttons=buttons, parse_mode='markdown')
            
        except Exception as e:
            logger.error(f"Ошибка отправки результата: {e}")
            await event.respond(f"✅ Анализ завершен, но возникла ошибка форматирования: {str(e)}")
    
    async def handle_quick_analysis(self, event):
        """Быстрый анализ последних сообщений"""
        await event.edit(
            "🔍 **Быстрый анализ**\n\n"
            "Анализ последних 50 сообщений из выбранного чата.\n"
            "Время выполнения: ~30 секунд\n\n"
            "Отправьте ID чата или используйте /chats для просмотра списка.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'back')]
            ],
            parse_mode='markdown'
        )
        
        # Устанавливаем режим быстрого анализа
        user_id = event.sender_id
        self.user_states[user_id] = {
            'state': 'waiting_chat',
            'analysis_type': 'quick',
            'limit': 50
        }
    
    async def handle_deep_analysis(self, event):
        """Глубокий анализ с большим объемом данных"""
        await event.edit(
            "📈 **Глубокий анализ**\n\n"
            "Детальный анализ до 200 сообщений с временной динамикой.\n"
            "Время выполнения: ~2-3 минуты\n\n"
            "Отправьте ID чата или используйте /chats для просмотра списка.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'back')]
            ],
            parse_mode='markdown'
        )
        
        user_id = event.sender_id
        self.user_states[user_id] = {
            'state': 'waiting_chat',
            'analysis_type': 'deep',
            'limit': 200
        }
    
    async def handle_voice_only(self, event):
        """Анализ только голосовых сообщений"""
        await event.edit(
            "🎤 **Анализ голосовых сообщений**\n\n"
            "Специальный анализ только голосовых сообщений:\n"
            "• Эмоциональные характеристики речи\n"
            "• Паттерны интонации\n"
            "• Длительность и частота\n\n"
            "Отправьте ID чата для анализа голосовых.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'back')]
            ],
            parse_mode='markdown'
        )
        
        user_id = event.sender_id
        self.user_states[user_id] = {
            'state': 'waiting_chat',
            'analysis_type': 'voice_only',
            'limit': 100
        }
    
    async def handle_text_only(self, event):
        """Анализ только текстовых сообщений"""
        await event.edit(
            "📝 **Анализ текстовых сообщений**\n\n"
            "Фокус на текстовом контенте:\n"
            "• Тематический анализ\n"
            "• Тональность и эмоции\n"
            "• Ключевые фразы и паттерны\n\n"
            "Отправьте ID чата для текстового анализа.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'back')]
            ],
            parse_mode='markdown'
        )
        
        user_id = event.sender_id
        self.user_states[user_id] = {
            'state': 'waiting_chat',
            'analysis_type': 'text_only',
            'limit': 150
        }
    
    async def handle_time_period(self, event, period):
        """Анализ за определенный период"""
        period_names = {
            'last_week': 'последнюю неделю',
            'last_month': 'последний месяц'
        }
        
        period_days = {
            'last_week': 7,
            'last_month': 30
        }
        
        await event.edit(
            f"📅 **Анализ за {period_names[period]}**\n\n"
            f"Анализ сообщений за последние {period_days[period]} дней.\n"
            "Включает временную динамику и тренды.\n\n"
            "Отправьте ID чата для анализа.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'back')]
            ],
            parse_mode='markdown'
        )
        
        user_id = event.sender_id
        self.user_states[user_id] = {
            'state': 'waiting_chat',
            'analysis_type': 'time_period',
            'period_days': period_days[period],
            'limit': 200
        }
    
    async def handle_show_chats(self, event):
        """Показать список чатов - сначала личные, потом кнопка для групп"""
        try:
            await event.edit("🔄 Загружаю ваши личные чаты...")
            
            # Получаем только личные чаты
            personal_chats = []
            group_chats = []
            channels = []
            
            async for dialog in self.user_client.iter_dialogs(limit=50):
                if dialog.is_user:
                    entity = dialog.entity
                    # Фильтруем ботов
                    if hasattr(entity, 'bot') and entity.bot:
                        continue  # Пропускаем ботов
                    
                    # Фильтруем по username (если есть username с bot)
                    if hasattr(entity, 'username') and entity.username:
                        if 'bot' in entity.username.lower():
                            continue  # Пропускаем ботов по username
                    
                    chat_info = {
                        'id': dialog.id,
                        'name': dialog.name[:25],
                        'unread': dialog.unread_count,
                        'username': getattr(entity, 'username', None)
                    }
                    personal_chats.append(chat_info)
                    
                elif dialog.is_group:
                    group_chats.append({'count': 1})  # Просто считаем
                elif dialog.is_channel:
                    channels.append({'count': 1})  # Просто считаем
            
            # Создаем кнопки - сначала личные чаты
            buttons = []
            
            # Личные чаты сразу показываем
            if personal_chats:
                for chat in personal_chats[:12]:  # Показываем до 12 личных чатов
                    chat_name = chat['name']
                    if chat['unread'] > 0:
                        chat_name += f" ({chat['unread']})"
                    
                    # Добавляем username если есть
                    if chat.get('username'):
                        chat_name = f"{chat_name} @{chat['username']}"
                    
                    buttons.append([Button.inline(
                        f"💬 {chat_name}", 
                        f"chat_{chat['id']}".encode()
                    )])
            
            # Дополнительные опции внизу
            additional_buttons = []
            
            # Если есть еще личные чаты
            if len(personal_chats) > 12:
                additional_buttons.append(Button.inline(f'📋 Еще личные ({len(personal_chats) - 12})', b'show_all_personal'))
            
            # Группы и каналы за кнопкой
            if group_chats or channels:
                group_count = len(group_chats)
                channel_count = len(channels)
                total_other = group_count + channel_count
                additional_buttons.append(Button.inline(f'👥 Группы и каналы ({total_other})', b'show_groups_channels'))
            
            # Размещаем дополнительные кнопки
            if additional_buttons:
                if len(additional_buttons) == 1:
                    buttons.append([additional_buttons[0]])
                else:
                    buttons.append(additional_buttons)
            
            buttons.append([Button.inline('◀️ Назад', b'back')])
            
            # Формируем сообщение
            if not personal_chats:
                message = "❌ **Личные чаты не найдены**\n\n🤖 Боты исключены из списка"
            else:
                message = f"💬 **Ваши личные чаты** ({len(personal_chats)})\n\n"
                message += f"🤖 Боты исключены\n"
                message += f"📱 Показано: {min(12, len(personal_chats))} из {len(personal_chats)}\n\n"
                message += "Выберите чат для анализа:"
            
            await event.edit(
                message,
                buttons=buttons,
                parse_mode='markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения списка чатов: {e}")
            await event.edit(f"❌ Ошибка: {str(e)}")
    
    async def handle_show_groups_channels(self, event):
        """Показать группы и каналы"""
        try:
            await event.edit("🔄 Загружаю группы и каналы...")
            
            group_chats = []
            channels = []
            
            async for dialog in self.user_client.iter_dialogs(limit=50):
                if dialog.is_group:
                    chat_info = {
                        'id': dialog.id,
                        'name': dialog.name[:25],
                        'unread': dialog.unread_count
                    }
                    group_chats.append(chat_info)
                    
                elif dialog.is_channel:
                    chat_info = {
                        'id': dialog.id,
                        'name': dialog.name[:25],
                        'unread': dialog.unread_count
                    }
                    channels.append(chat_info)
            
            buttons = []
            
            # Групповые чаты
            if group_chats:
                buttons.append([Button.inline("👥 ГРУППОВЫЕ ЧАТЫ", b"category_groups")])
                for chat in group_chats[:8]:  # Показываем до 8 групп
                    chat_name = chat['name']
                    if chat['unread'] > 0:
                        chat_name += f" ({chat['unread']})"
                    
                    buttons.append([Button.inline(
                        f"👥 {chat_name}", 
                        f"chat_{chat['id']}".encode()
                    )])
            
            # Каналы
            if channels:
                buttons.append([Button.inline("📢 КАНАЛЫ", b"category_channels")])
                for chat in channels[:6]:  # Показываем до 6 каналов
                    chat_name = chat['name']
                    if chat['unread'] > 0:
                        chat_name += f" ({chat['unread']})"
                    
                    buttons.append([Button.inline(
                        f"📢 {chat_name}", 
                        f"chat_{chat['id']}".encode()
                    )])
            
            # Дополнительные опции
            additional_buttons = []
            if len(group_chats) > 8:
                additional_buttons.append(Button.inline(f'👥 Все группы ({len(group_chats)})', b'show_all_groups'))
            if len(channels) > 6:
                additional_buttons.append(Button.inline(f'📢 Все каналы ({len(channels)})', b'show_all_channels'))
            
            if additional_buttons:
                if len(additional_buttons) == 1:
                    buttons.append([additional_buttons[0]])
                else:
                    buttons.append(additional_buttons)
            
            buttons.append([Button.inline('◀️ К личным чатам', b'show_chats')])
            
            total = len(group_chats) + len(channels)
            message = f"👥 **Группы и каналы** ({total})\n\n"
            message += f"👥 Групп: {len(group_chats)}\n"
            message += f"📢 Каналов: {len(channels)}\n\n"
            message += "Выберите чат для анализа:"
            
            await event.edit(
                message,
                buttons=buttons,
                parse_mode='markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения групп и каналов: {e}")
            await event.edit(f"❌ Ошибка: {str(e)}")
    
    async def handle_show_all_personal(self, event):
        """Показать все личные чаты"""
        try:
            await event.edit("🔄 Загружаю все личные чаты...")
            
            personal_chats = []
            async for dialog in self.user_client.iter_dialogs(limit=100):
                if dialog.is_user:
                    entity = dialog.entity
                    
                    # Фильтруем ботов
                    if hasattr(entity, 'bot') and entity.bot:
                        continue  # Пропускаем ботов
                    
                    # Фильтруем по username (если есть username с bot)
                    if hasattr(entity, 'username') and entity.username:
                        if 'bot' in entity.username.lower():
                            continue  # Пропускаем ботов по username
                    
                    personal_chats.append({
                        'id': dialog.id,
                        'name': dialog.name[:20],
                        'unread': dialog.unread_count,
                        'username': getattr(entity, 'username', None)
                    })
            
            if not personal_chats:
                await event.edit(
                    "❌ **Личные чаты не найдены**\n\n"
                    "Возможные причины:\n"
                    "• Все диалоги с ботами (исключены из списка)\n"
                    "• Нет активных личных чатов\n"
                    "• Ограничения доступа к диалогам",
                    buttons=[[Button.inline('◀️ К списку чатов', b'show_chats')]],
                    parse_mode='markdown'
                )
                return
            
            buttons = []
            for chat in personal_chats[:20]:  # Показываем до 20 чатов
                chat_name = chat['name']
                if chat['unread'] > 0:
                    chat_name += f" ({chat['unread']})"
                
                # Добавляем username если есть
                if chat.get('username'):
                    chat_name += f" @{chat['username']}"
                
                buttons.append([Button.inline(
                    f"💬 {chat_name}", 
                    f"chat_{chat['id']}".encode()
                )])
            
            # Если чатов больше 20, добавляем кнопку "Показать еще"
            if len(personal_chats) > 20:
                buttons.append([Button.inline(f'📋 Показать еще ({len(personal_chats) - 20})', b'show_more_personal')])
            
            buttons.append([Button.inline('◀️ К списку чатов', b'show_chats')])
            
            await event.edit(
                f"👤 **Все личные чаты** ({len(personal_chats)})\n\n"
                f"🤖 Боты исключены из списка\n"
                f"📱 Показано: {min(20, len(personal_chats))} из {len(personal_chats)}\n\n"
                "Выберите чат для анализа:",
                buttons=buttons,
                parse_mode='markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения личных чатов: {e}")
            await event.edit(f"❌ Ошибка: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def handle_show_all_groups(self, event):
        """Показать все групповые чаты"""
        try:
            await event.edit("🔄 Загружаю все групповые чаты...")
            
            group_chats = []
            async for dialog in self.user_client.iter_dialogs(limit=50):
                if dialog.is_group:
                    group_chats.append({
                        'id': dialog.id,
                        'name': dialog.name[:20],
                        'unread': dialog.unread_count
                    })
            
            buttons = []
            for chat in group_chats[:15]:  # Максимум 15 чатов
                chat_name = chat['name']
                if chat['unread'] > 0:
                    chat_name += f" ({chat['unread']})"
                
                buttons.append([Button.inline(
                    f"👥 {chat_name}", 
                    f"chat_{chat['id']}".encode()
                )])
            
            buttons.append([Button.inline('◀️ К списку чатов', b'show_chats')])
            
            await event.edit(
                f"👥 **Все групповые чаты** ({len(group_chats)})\n\n"
                "Выберите чат для анализа:",
                buttons=buttons,
                parse_mode='markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения групповых чатов: {e}")
            await event.edit(f"❌ Ошибка: {str(e)}")
    
    async def handle_show_all_channels(self, event):
        """Показать все каналы"""
        try:
            await event.edit("🔄 Загружаю все каналы...")
            
            channels = []
            async for dialog in self.user_client.iter_dialogs(limit=100):
                if dialog.is_channel:
                    channels.append({
                        'id': dialog.id,
                        'name': dialog.name[:20],
                        'unread': dialog.unread_count
                    })
            
            if not channels:
                await event.edit(
                    "❌ **Каналы не найдены**\n\n"
                    "Возможные причины:\n"
                    "• Нет подписок на каналы\n"
                    "• Ограничения доступа к каналам",
                    buttons=[[Button.inline('◀️ К группам и каналам', b'show_groups_channels')]],
                    parse_mode='markdown'
                )
                return
            
            buttons = []
            for chat in channels[:20]:  # Показываем до 20 каналов
                chat_name = chat['name']
                if chat['unread'] > 0:
                    chat_name += f" ({chat['unread']})"
                
                buttons.append([Button.inline(
                    f"📢 {chat_name}", 
                    f"chat_{chat['id']}".encode()
                )])
            
            if len(channels) > 20:
                buttons.append([Button.inline(f'📋 Показать еще ({len(channels) - 20})', b'show_more_channels')])
            
            buttons.append([Button.inline('◀️ К группам и каналам', b'show_groups_channels')])
            
            await event.edit(
                f"📢 **Все каналы** ({len(channels)})\n\n"
                f"📱 Показано: {min(20, len(channels))} из {len(channels)}\n\n"
                "Выберите канал для анализа:",
                buttons=buttons,
                parse_mode='markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения каналов: {e}")
            await event.edit(f"❌ Ошибка: {str(e)}")
    
    async def handle_popular_topics(self, event):
        """Анализ популярных тем"""
        await event.edit(
            "🔥 **Популярные темы в ваших диалогах**\n\n"
            "Автоматический поиск самых обсуждаемых тем:\n"
            "• Частота упоминаний\n"
            "• Эмоциональная окраска\n"
            "• Временные тренды\n\n"
            "Отправьте ID чата для анализа популярных тем.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ К темам', b'topics')]
            ],
            parse_mode='markdown'
        )
        
        user_id = event.sender_id
        self.user_states[user_id] = {
            'state': 'waiting_chat',
            'analysis_type': 'popular_topics',
            'limit': 200
        }
    
    async def handle_personal_insights(self, event):
        """Персональные инсайты"""
        await event.edit(
            "🎯 **Персональные инсайты**\n\n"
            "Глубокий анализ ваших коммуникационных паттернов:\n"
            "• Стиль общения\n"
            "• Эмоциональные реакции\n"
            "• Предпочтения в темах\n"
            "• Динамика настроения\n\n"
            "Отправьте ID чата для персонального анализа.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ К темам', b'topics')]
            ],
            parse_mode='markdown'
        )
        
        user_id = event.sender_id
        self.user_states[user_id] = {
            'state': 'waiting_chat',
            'analysis_type': 'personal_insights',
            'limit': 200
        }
    
    async def handle_help(self, event):
        """Обработка помощи"""
        help_text = """
ℹ️ **Помощь по использованию бота**

**Основные команды:**
/start - Главное меню
/chats - Список ваших чатов
/help - Эта справка

**Как использовать:**

1️⃣ Выберите "Анализ по темам" в меню
2️⃣ Выберите интересующую тему
3️⃣ Используйте /chats для просмотра списка чатов
4️⃣ Отправьте ID чата для анализа

**Темы анализа:**
• 💼 Работа и карьера
• 👥 Отношения
• 🎯 Цели и планы
• 😊 Эмоции и настроение
• 🧠 Саморазвитие
• 💭 Общий анализ

**Что вы получите:**
✓ Саммари диалога по теме
✓ Ключевые инсайты
✓ Эмоциональную динамику
✓ Анализ голосовых сообщений

🔒 Все данные обрабатываются локально и конфиденциально.
"""
        
        await event.edit(
            help_text,
            buttons=[[Button.inline('◀️ Назад', b'back')]],
            parse_mode='markdown'
        )
    
    async def handle_chat_selection(self, event, chat_id: int):
        """Обработка выбора чата через кнопку"""
        user_id = event.sender_id
        user_state = self.user_states.get(user_id, {})
        analysis_type = user_state.get('analysis_type', 'general')
        
        # Получаем информацию о чате
        try:
            chat = await self.user_client.get_entity(chat_id)
            chat_name = getattr(chat, 'first_name', getattr(chat, 'title', 'Неизвестный чат'))
        except:
            chat_name = f"Чат {chat_id}"
        
        await event.edit(
            f"🔄 Начинаю анализ чата **{chat_name}**\n"
            f"📊 Тип анализа: {self.get_analysis_type_name(analysis_type)}\n\n"
            f"⏳ Это может занять некоторое время...",
            parse_mode='markdown'
        )
        
        # Запускаем анализ
        try:
            result = await self.analyze_chat_by_type(chat_id, user_state)
            
            if result.get('success'):
                await self.send_analysis_result(event, result)
            else:
                await event.respond(f"❌ Ошибка анализа: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Ошибка анализа чата: {e}")
            await event.respond(f"❌ Критическая ошибка: {str(e)}")
        
        # Очищаем состояние
        if user_id in self.user_states:
            del self.user_states[user_id]
    
    def get_analysis_type_name(self, analysis_type: str) -> str:
        """Получить название типа анализа"""
        type_names = {
            'quick': '🔍 Быстрый анализ',
            'deep': '📈 Глубокий анализ',
            'voice_only': '🎤 Только голосовые',
            'text_only': '📝 Только текст',
            'time_period': '📅 По периоду',
            'popular_topics': '🔥 Популярные темы',
            'personal_insights': '🎯 Персональные инсайты',
            'general': '💭 Общий анализ'
        }
        return type_names.get(analysis_type, '💭 Общий анализ')
    
    async def analyze_chat_by_type(self, chat_id: int, user_state: dict) -> dict:
        """Анализ чата в зависимости от типа"""
        analysis_type = user_state.get('analysis_type', 'general')
        limit = user_state.get('limit', 100)
        
        try:
            # Собираем сообщения
            messages = await self.collect_chat_messages(chat_id, limit=limit)
            
            if not messages:
                return {'success': False, 'error': 'Не найдено сообщений в чате'}
            
            # Фильтруем по типу анализа
            if analysis_type == 'voice_only':
                filtered_messages = [msg for msg in messages if msg.get('type') == 'voice']
            elif analysis_type == 'text_only':
                filtered_messages = [msg for msg in messages if msg.get('type') == 'text']
            elif analysis_type == 'time_period':
                period_days = user_state.get('period_days', 7)
                filtered_messages = self.filter_by_time_period(messages, period_days)
            else:
                filtered_messages = messages
            
            if not filtered_messages:
                return {
                    'success': False, 
                    'error': f'Не найдено сообщений для типа анализа "{self.get_analysis_type_name(analysis_type)}"'
                }
            
            # Выполняем анализ
            result = await self.analyzer.create_combined_analysis(
                filtered_messages,
                participant_names=['Вы', 'Собеседник']
            )
            
            if result.get('success'):
                result['analysis_type'] = analysis_type
                result['analysis_type_name'] = self.get_analysis_type_name(analysis_type)
                result['total_messages_in_chat'] = len(messages)
                result['filtered_messages'] = len(filtered_messages)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка анализа по типу: {e}")
            return {'success': False, 'error': str(e)}
    
    def filter_by_time_period(self, messages: list, days: int) -> list:
        """Фильтрация сообщений по временному периоду"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []
        
        for msg in messages:
            try:
                msg_date = datetime.fromisoformat(msg.get('date', '').replace('Z', '+00:00'))
                if msg_date >= cutoff_date:
                    filtered.append(msg)
            except:
                continue
        
        return filtered
    
    async def handle_global_analysis(self, event):
        """Глобальный анализ по всем чатам"""
        await event.edit(
            "🌍 **Глобальный самоанализ**\n\n"
            "Анализ всех ваших чатов за выбранный период:\n"
            "• Общие коммуникационные паттерны\n"
            "• Эмоциональная динамика\n"
            "• Активность по типам чатов\n"
            "• Топ-темы и инсайты\n\n"
            "Выберите период для анализа:",
            buttons=[
                [
                    Button.inline('📅 За неделю', b'global_week'),
                    Button.inline('📆 За месяц', b'global_month')
                ],
                [
                    Button.inline('🗓️ За 3 месяца', b'global_3months'),
                    Button.inline('📊 За все время', b'global_all')
                ],
                [
                    Button.inline('🎯 Только активные чаты', b'global_active')
                ],
                [Button.inline('◀️ Назад', b'back')]
            ],
            parse_mode='markdown'
        )
    
    async def handle_global_period(self, event, period_type: str):
        """Обработка выбора периода для глобального анализа"""
        period_configs = {
            'global_week': {'days': 7, 'name': 'неделю', 'limit_per_chat': 30},
            'global_month': {'days': 30, 'name': 'месяц', 'limit_per_chat': 50},
            'global_3months': {'days': 90, 'name': '3 месяца', 'limit_per_chat': 100},
            'global_all': {'days': 365, 'name': 'все время', 'limit_per_chat': 200},
            'global_active': {'days': 30, 'name': 'месяц (активные)', 'limit_per_chat': 100}
        }
        
        config = period_configs.get(period_type)
        if not config:
            await event.answer("❌ Неизвестный период")
            return
        
        await event.edit(
            f"🔄 **Запуск глобального анализа за {config['name']}**\n\n"
            f"⏳ Это займет 2-5 минут...\n"
            f"📊 Анализируем все ваши чаты\n"
            f"🎯 Ищем паттерны и инсайты\n\n"
            f"Пожалуйста, подождите...",
            parse_mode='markdown'
        )
        
        # Запускаем глобальный анализ
        try:
            result = await self.perform_global_analysis(config)
            
            if result.get('success'):
                await self.send_global_analysis_result(event, result, config['name'])
            else:
                await event.respond(f"❌ Ошибка глобального анализа: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Ошибка глобального анализа: {e}")
            await event.respond(f"❌ Критическая ошибка: {str(e)}")
    
    async def perform_global_analysis(self, config: dict) -> dict:
        """Выполнение глобального анализа всех чатов"""
        try:
            logger.info(f"🌍 Начинаем глобальный анализ за {config['name']}")
            
            # Собираем все чаты
            all_chats = []
            personal_chats = []
            group_chats = []
            channels = []
            
            async for dialog in self.user_client.iter_dialogs(limit=50):
                chat_info = {
                    'id': dialog.id,
                    'name': dialog.name,
                    'type': 'personal' if dialog.is_user else 'group' if dialog.is_group else 'channel',
                    'unread': dialog.unread_count
                }
                
                all_chats.append(chat_info)
                
                if dialog.is_user:
                    personal_chats.append(chat_info)
                elif dialog.is_group:
                    group_chats.append(chat_info)
                elif dialog.is_channel:
                    channels.append(chat_info)
            
            logger.info(f"📊 Найдено чатов: {len(all_chats)} (личных: {len(personal_chats)}, групп: {len(group_chats)}, каналов: {len(channels)})")
            
            # Фильтруем активные чаты если нужно
            if 'активные' in config['name']:
                active_chats = [chat for chat in all_chats if chat['unread'] > 0 or chat['type'] == 'personal'][:15]
            else:
                active_chats = all_chats[:20]  # Ограничиваем для производительности
            
            # Собираем сообщения из всех чатов
            all_messages = []
            chat_stats = {}
            
            for i, chat in enumerate(active_chats, 1):
                try:
                    logger.info(f"📥 Обрабатываем чат {i}/{len(active_chats)}: {chat['name']}")
                    
                    messages = await self.collect_chat_messages(
                        chat['id'], 
                        limit=config['limit_per_chat']
                    )
                    
                    # Фильтруем по времени
                    filtered_messages = self.filter_by_time_period(messages, config['days'])
                    
                    if filtered_messages:
                        # Добавляем метаданные чата к сообщениям
                        for msg in filtered_messages:
                            msg['source_chat_id'] = chat['id']
                            msg['source_chat_name'] = chat['name']
                            msg['source_chat_type'] = chat['type']
                        
                        all_messages.extend(filtered_messages)
                        
                        chat_stats[chat['id']] = {
                            'name': chat['name'],
                            'type': chat['type'],
                            'message_count': len(filtered_messages),
                            'text_count': len([m for m in filtered_messages if m.get('type') == 'text']),
                            'voice_count': len([m for m in filtered_messages if m.get('type') == 'voice'])
                        }
                
                except Exception as e:
                    logger.error(f"Ошибка обработки чата {chat['name']}: {e}")
                    continue
            
            if not all_messages:
                return {'success': False, 'error': 'Не найдено сообщений за указанный период'}
            
            logger.info(f"✅ Собрано {len(all_messages)} сообщений из {len(chat_stats)} чатов")
            
            # Выполняем комплексный анализ
            analysis_result = await self.analyzer.create_combined_analysis(
                all_messages,
                participant_names=['Вы', 'Собеседники']
            )
            
            if analysis_result.get('success'):
                # Добавляем глобальную статистику
                global_stats = self._create_global_statistics(all_messages, chat_stats, config)
                
                return {
                    'success': True,
                    'global_analysis': analysis_result,
                    'global_stats': global_stats,
                    'chat_stats': chat_stats,
                    'period_config': config,
                    'total_chats_analyzed': len(chat_stats),
                    'total_messages': len(all_messages)
                }
            else:
                return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка глобального анализа: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_global_statistics(self, all_messages: list, chat_stats: dict, config: dict) -> dict:
        """Создание глобальной статистики"""
        try:
            from collections import Counter
            from datetime import datetime, timedelta
            
            # Общая статистика
            total_messages = len(all_messages)
            text_messages = len([m for m in all_messages if m.get('type') == 'text'])
            voice_messages = len([m for m in all_messages if m.get('type') == 'voice'])
            
            # Статистика по типам чатов
            chat_type_stats = Counter()
            for chat_id, stats in chat_stats.items():
                chat_type_stats[stats['type']] += stats['message_count']
            
            # Топ активных чатов
            top_chats = sorted(
                chat_stats.items(), 
                key=lambda x: x[1]['message_count'], 
                reverse=True
            )[:10]
            
            # Средняя активность
            days_in_period = config['days']
            avg_messages_per_day = total_messages / days_in_period if days_in_period > 0 else 0
            
            return {
                'total_messages': total_messages,
                'text_messages': text_messages,
                'voice_messages': voice_messages,
                'total_chats': len(chat_stats),
                'chat_type_distribution': dict(chat_type_stats),
                'top_active_chats': top_chats,
                'avg_messages_per_day': avg_messages_per_day,
                'period_days': days_in_period,
                'voice_text_ratio': voice_messages / text_messages if text_messages > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания глобальной статистики: {e}")
            return {}
    
    async def send_global_analysis_result(self, event, result: dict, period_name: str):
        """Отправка результата глобального анализа"""
        try:
            global_stats = result.get('global_stats', {})
            analysis = result.get('global_analysis', {})
            
            # Основная статистика
            response = f"🌍 **Глобальный самоанализ за {period_name}**\n\n"
            
            response += f"📊 **Общая статистика:**\n"
            response += f"• Всего сообщений: {global_stats.get('total_messages', 0)}\n"
            response += f"• Проанализировано чатов: {global_stats.get('total_chats', 0)}\n"
            response += f"• Текстовых сообщений: {global_stats.get('text_messages', 0)}\n"
            response += f"• Голосовых сообщений: {global_stats.get('voice_messages', 0)}\n"
            response += f"• Среднее в день: {global_stats.get('avg_messages_per_day', 0):.1f}\n\n"
            
            # Распределение по типам чатов
            chat_distribution = global_stats.get('chat_type_distribution', {})
            if chat_distribution:
                response += f"📱 **Активность по типам чатов:**\n"
                for chat_type, count in chat_distribution.items():
                    emoji = {'personal': '👤', 'group': '👥', 'channel': '📢'}.get(chat_type, '💬')
                    response += f"• {emoji} {chat_type.title()}: {count} сообщений\n"
                response += "\n"
            
            # Топ активных чатов
            top_chats = global_stats.get('top_active_chats', [])
            if top_chats:
                response += f"🔥 **Топ-5 активных чатов:**\n"
                for i, (chat_id, stats) in enumerate(top_chats[:5], 1):
                    emoji = {'personal': '👤', 'group': '👥', 'channel': '📢'}.get(stats['type'], '💬')
                    response += f"{i}. {emoji} {stats['name'][:20]}: {stats['message_count']} сообщений\n"
                response += "\n"
            
            # Инсайты из анализа
            insights = analysis.get('insights', [])
            if insights:
                response += f"💡 **Ключевые инсайты:**\n"
                for insight in insights[:5]:
                    response += f"• {insight}\n"
                response += "\n"
            
            # Саммари диалогов
            dialog_summary = analysis.get('dialog_summary', {})
            if dialog_summary:
                summary_data = dialog_summary.get('summary', {})
                if isinstance(summary_data, dict):
                    # Основные темы
                    main_topics = summary_data.get('main_topics', [])
                    if main_topics:
                        response += f"📌 **Главные темы общения:**\n"
                        for topic in main_topics[:5]:
                            response += f"  • {topic}\n"
                        response += "\n"
                    
                    # Общая тональность
                    overall_tone = summary_data.get('overall_tone')
                    if overall_tone:
                        response += f"😊 **Общая тональность:** {overall_tone}\n\n"
            
            response += f"⏰ Анализ выполнен: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            # Кнопки для дополнительных действий
            buttons = [
                [
                    Button.inline('🔄 Другой период', b'global_analysis'),
                    Button.inline('📊 Детальный анализ', b'deep_analysis')
                ],
                [Button.inline('🏠 Главное меню', b'back')]
            ]
            
            await event.respond(response, buttons=buttons, parse_mode='markdown')
            
        except Exception as e:
            logger.error(f"Ошибка отправки глобального результата: {e}")
            await event.respond(f"✅ Глобальный анализ завершен, но возникла ошибка форматирования: {str(e)}")

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
            
            @self.bot_client.on(events.NewMessage(pattern='/chats'))
            async def chats_handler(event):
                await self.handle_chats_list(event)
            
            @self.bot_client.on(events.NewMessage(pattern='/help'))
            async def help_handler(event):
                await self.handle_help(event)
            
            # Обработчик ID чата
            @self.bot_client.on(events.NewMessage)
            async def message_handler(event):
                if not event.text.startswith('/'):
                    await self.handle_chat_id(event)
            
            # Обработчики кнопок
            @self.bot_client.on(events.CallbackQuery)
            async def callback_handler(event):
                data = event.data.decode()
                
                if data == 'topics':
                    await self.handle_topics(event)
                elif data.startswith('topic_'):
                    topic_id = data.split('_')[1]
                    await self.handle_topic_selection(event, topic_id)
                elif data == 'select_chat':
                    await self.handle_select_chat(event)
                elif data == 'quick_analysis':
                    await self.handle_quick_analysis(event)
                elif data == 'deep_analysis':
                    await self.handle_deep_analysis(event)
                elif data == 'voice_only':
                    await self.handle_voice_only(event)
                elif data == 'text_only':
                    await self.handle_text_only(event)
                elif data == 'global_analysis':
                    await self.handle_global_analysis(event)
                elif data.startswith('global_'):
                    await self.handle_global_period(event, data)
                elif data == 'last_week':
                    await self.handle_time_period(event, 'last_week')
                elif data == 'last_month':
                    await self.handle_time_period(event, 'last_month')
                elif data == 'show_chats':
                    await self.handle_show_chats(event)
                elif data == 'show_groups_channels':
                    await self.handle_show_groups_channels(event)
                elif data == 'show_all_personal':
                    await self.handle_show_all_personal(event)
                elif data == 'show_all_groups':
                    await self.handle_show_all_groups(event)
                elif data == 'show_all_channels':
                    await self.handle_show_all_channels(event)
                elif data.startswith('category_'):
                    await event.answer("ℹ️ Выберите конкретный чат из списка ниже")
                elif data.startswith('chat_'):
                    chat_id = int(data.split('_')[1])
                    await self.handle_chat_selection(event, chat_id)
                elif data == 'popular_topics':
                    await self.handle_popular_topics(event)
                elif data == 'personal_insights':
                    await self.handle_personal_insights(event)
                elif data == 'history':
                    await event.answer("📈 История анализов пока не реализована")
                elif data == 'help':
                    await self.handle_help(event)
                elif data == 'back':
                    await event.edit(
                        "🔮 **Главное меню**\n\nВыберите действие:",
                        buttons=self.get_main_menu(),
                        parse_mode='markdown'
                    )
                else:
                    await event.answer("⚠️ Неизвестная команда")
            
            logger.info("🤖 Бот самоанализа запущен и готов к работе!")
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
    bot = SelfAnalysisBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main())
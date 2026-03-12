"""Обработчики чатов: листинг, выбор, сбор сообщений"""

import logging
from datetime import datetime, timedelta

from telethon import Button

logger = logging.getLogger(__name__)


class ChatHandlerMixin:
    """Миксин для работы с чатами и сбором сообщений"""

    async def handle_show_chats(self, event):
        """Показать список чатов - сначала личные, потом кнопка для групп"""
        user_client = await self.require_user_session(event, "просмотра чатов")
        if not user_client:
            return

        try:
            await event.edit("🔄 Загружаю ваши личные чаты...")

            personal_chats = []
            group_chats = []
            channels = []

            async for dialog in user_client.iter_dialogs(limit=50):
                if dialog.is_user:
                    entity = dialog.entity
                    if hasattr(entity, 'bot') and entity.bot:
                        continue
                    if hasattr(entity, 'username') and entity.username:
                        if 'bot' in entity.username.lower():
                            continue

                    personal_chats.append({
                        'id': dialog.id,
                        'name': dialog.name[:25],
                        'unread': dialog.unread_count,
                        'username': getattr(entity, 'username', None)
                    })
                elif dialog.is_group:
                    group_chats.append({'count': 1})
                elif dialog.is_channel:
                    channels.append({'count': 1})

            buttons = []

            if personal_chats:
                for chat in personal_chats[:12]:
                    chat_name = chat['name']
                    if chat['unread'] > 0:
                        chat_name += f" ({chat['unread']})"
                    if chat.get('username'):
                        chat_name = f"{chat_name} @{chat['username']}"

                    buttons.append([Button.inline(
                        f"💬 {chat_name}",
                        f"chat_{chat['id']}".encode()
                    )])

            additional_buttons = []
            if len(personal_chats) > 12:
                additional_buttons.append(
                    Button.inline(f'📋 Еще личные ({len(personal_chats) - 12})', b'show_all_personal')
                )
            if group_chats or channels:
                total_other = len(group_chats) + len(channels)
                additional_buttons.append(
                    Button.inline(f'👥 Группы и каналы ({total_other})', b'show_groups_channels')
                )

            if additional_buttons:
                if len(additional_buttons) == 1:
                    buttons.append([additional_buttons[0]])
                else:
                    buttons.append(additional_buttons)

            buttons.append([Button.inline('◀️ Назад', b'category_self_analysis')])

            if not personal_chats:
                message = "❌ **Личные чаты не найдены**\n\n🤖 Боты исключены из списка"
            else:
                message = f"💬 **Ваши личные чаты** ({len(personal_chats)})\n\n"
                message += f"🤖 Боты исключены\n"
                message += f"📱 Показано: {min(12, len(personal_chats))} из {len(personal_chats)}\n\n"
                message += "Выберите чат для анализа:"

            await event.edit(message, buttons=buttons, parse_mode='markdown')

        except Exception as e:
            logger.error(f"Ошибка получения списка чатов: {e}")
            await event.edit(f"❌ Ошибка: {str(e)}")

    async def handle_chat_selection(self, event, chat_id: int):
        """Обработка выбора чата через кнопку"""
        user_client = await self.require_user_session(event, "анализа чата")
        if not user_client:
            return

        user_id = event.sender_id
        user_state = self.user_states.get(user_id, {})
        analysis_type = user_state.get('analysis_type', 'general')

        try:
            chat = await user_client.get_entity(chat_id)
            chat_name = getattr(chat, 'first_name', getattr(chat, 'title', 'Неизвестный чат'))
        except Exception:
            chat_name = f"Чат {chat_id}"

        await event.edit(
            f"🔄 Начинаю анализ чата **{chat_name}**\n"
            f"📊 Тип анализа: {self.get_analysis_type_name(analysis_type)}\n\n"
            f"⏳ Это может занять некоторое время...",
            parse_mode='markdown'
        )

        try:
            result = await self.analyze_chat_by_type(chat_id, user_state, user_client)
            if result.get('success'):
                await self.send_analysis_result(event, result)
            else:
                await event.respond(f"❌ Ошибка анализа: {result.get('error')}")
        except Exception as e:
            logger.error(f"Ошибка анализа чата: {e}")
            await event.respond(f"❌ Критическая ошибка: {str(e)}")

        if user_id in self.user_states:
            del self.user_states[user_id]

        if hasattr(self, "post_request_session_cleanup"):
            await self.post_request_session_cleanup(user_id, event)

    async def analyze_chat_by_type(self, chat_id: int, user_state: dict, user_client) -> dict:
        """Анализ чата в зависимости от типа"""
        analysis_type = user_state.get('analysis_type', 'general')
        limit = user_state.get('limit', 100)

        try:
            messages = await self.collect_chat_messages(chat_id, user_client=user_client, limit=limit)

            if not messages:
                return {'success': False, 'error': 'Не найдено сообщений в чате'}

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

    async def collect_chat_messages(self, chat_id: int, user_client, limit: int = 200) -> list:
        """Сбор сообщений из любого типа чата"""
        try:
            messages = []
            chat = await user_client.get_entity(chat_id)

            logger.info(f"📥 Сбор сообщений из чата: {getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))}")

            async for message in user_client.iter_messages(chat, limit=limit):
                msg_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'from_id': getattr(message.from_id, 'user_id', None) if message.from_id else None,
                    'chat_type': 'group' if hasattr(chat, 'participants_count') else 'personal'
                }

                if hasattr(chat, 'participants_count'):
                    try:
                        sender = await message.get_sender()
                        if sender:
                            msg_data['sender_name'] = getattr(sender, 'first_name', 'Unknown')
                    except Exception:
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

    def filter_by_time_period(self, messages: list, days: int) -> list:
        """Фильтрация сообщений по временному периоду"""
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []

        for msg in messages:
            try:
                msg_date = datetime.fromisoformat(msg.get('date', '').replace('Z', '+00:00'))
                if msg_date.replace(tzinfo=None) >= cutoff_date:
                    filtered.append(msg)
            except (ValueError, TypeError):
                continue

        return filtered

    async def handle_show_groups_channels(self, event):
        """Показать группы и каналы"""
        user_client = await self.require_user_session(event, "просмотра групп и каналов")
        if not user_client:
            return

        try:
            await event.edit("🔄 Загружаю группы и каналы...")

            group_chats = []
            channels = []

            async for dialog in user_client.iter_dialogs(limit=50):
                if dialog.is_group:
                    group_chats.append({
                        'id': dialog.id,
                        'name': dialog.name[:25],
                        'unread': dialog.unread_count
                    })
                elif dialog.is_channel:
                    channels.append({
                        'id': dialog.id,
                        'name': dialog.name[:25],
                        'unread': dialog.unread_count
                    })

            buttons = []

            if group_chats:
                buttons.append([Button.inline("👥 ГРУППОВЫЕ ЧАТЫ", b"category_groups")])
                for chat in group_chats[:8]:
                    chat_name = chat['name']
                    if chat['unread'] > 0:
                        chat_name += f" ({chat['unread']})"
                    buttons.append([Button.inline(
                        f"👥 {chat_name}",
                        f"chat_{chat['id']}".encode()
                    )])

            if channels:
                buttons.append([Button.inline("📢 КАНАЛЫ", b"category_channels")])
                for chat in channels[:6]:
                    chat_name = chat['name']
                    if chat['unread'] > 0:
                        chat_name += f" ({chat['unread']})"
                    buttons.append([Button.inline(
                        f"📢 {chat_name}",
                        f"chat_{chat['id']}".encode()
                    )])

            buttons.append([Button.inline('◀️ К личным чатам', b'show_chats')])

            total = len(group_chats) + len(channels)
            message = f"👥 **Группы и каналы** ({total})\n\n"
            message += f"👥 Групп: {len(group_chats)}\n"
            message += f"📢 Каналов: {len(channels)}\n\n"
            message += "Выберите чат для анализа:"

            await event.edit(message, buttons=buttons, parse_mode='markdown')

        except Exception as e:
            logger.error(f"Ошибка получения групп и каналов: {e}")
            await event.edit(f"❌ Ошибка: {str(e)}")

    async def handle_show_all_personal(self, event):
        """Показать все личные чаты"""
        user_client = await self.require_user_session(event, "просмотра личных чатов")
        if not user_client:
            return

        try:
            await event.edit("🔄 Загружаю все личные чаты...")

            personal_chats = []
            async for dialog in user_client.iter_dialogs(limit=100):
                if dialog.is_user:
                    entity = dialog.entity
                    if hasattr(entity, 'bot') and entity.bot:
                        continue
                    if hasattr(entity, 'username') and entity.username:
                        if 'bot' in entity.username.lower():
                            continue

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
            for chat in personal_chats[:20]:
                chat_name = chat['name']
                if chat['unread'] > 0:
                    chat_name += f" ({chat['unread']})"
                if chat.get('username'):
                    chat_name += f" @{chat['username']}"
                buttons.append([Button.inline(
                    f"💬 {chat_name}",
                    f"chat_{chat['id']}".encode()
                )])

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

    async def handle_show_all_groups(self, event):
        """Показать все групповые чаты"""
        await event.edit(
            "👥 **Все групповые чаты**\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'show_groups_channels')]],
            parse_mode='markdown'
        )

    async def handle_show_all_channels(self, event):
        """Показать все каналы"""
        await event.edit(
            "📢 **Все каналы**\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'show_groups_channels')]],
            parse_mode='markdown'
        )

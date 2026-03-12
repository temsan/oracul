"""Форматирование и отправка результатов анализа"""

import logging
from datetime import datetime

from telethon import Button

logger = logging.getLogger(__name__)


class FormatterMixin:
    """Миксин для форматирования результатов"""

    def get_analysis_type_name(self, analysis_type: str) -> str:
        """Получить название типа анализа"""
        type_names = {
            'quick': '🔍 Быстрый анализ',
            'deep': '📈 Глубокий анализ',
            'voice_only': '🎤 Только голосовые',
            'text_only': '📝 Только текст',
            'time_period': '📅 По периоду',
            'general': '💭 Общий анализ'
        }
        return type_names.get(analysis_type, '💭 Общий анализ')

    async def send_analysis_result(self, event, result: dict):
        """Отправка результата анализа"""
        try:
            analysis_type_name = result.get('analysis_type_name', 'Анализ')
            stats = result.get('statistics', {})

            response = f"✅ **{analysis_type_name}**\n\n"
            response += f"📊 **Статистика:**\n"
            response += f"• Всего сообщений в чате: {result.get('total_messages_in_chat', 0)}\n"
            response += f"• Проанализировано: {result.get('filtered_messages', 0)}\n"
            response += f"• Текстовых: {stats.get('text_messages', 0)}\n"
            response += f"• Голосовых: {stats.get('voice_messages', 0)}\n"

            chat_type = result.get('chat_type', 'unknown')
            if chat_type == 'group':
                response += f"• Тип чата: 👥 Групповой\n"
            else:
                response += f"• Тип чата: 👤 Личный\n"

            response += "\n"

            dialog_summary = result.get('dialog_summary', {})
            if dialog_summary:
                summary_data = dialog_summary.get('summary', {})

                if isinstance(summary_data, dict):
                    response += "💡 **Ключевые инсайты:**\n"

                    main_topics = summary_data.get('main_topics', [])
                    if main_topics:
                        response += "\n📌 Основные темы:\n"
                        for topic in main_topics[:3]:
                            response += f"  • {topic}\n"

                    overall_tone = summary_data.get('overall_tone')
                    if overall_tone:
                        response += f"\n😊 Общая тональность: {overall_tone}\n"

                    summary_text = summary_data.get('summary_text')
                    if summary_text:
                        response += f"\n📝 **Краткое саммари:**\n{summary_text}\n"

            insights = result.get('insights', [])
            if insights:
                response += "\n\n🎯 **Общие наблюдения:**\n"
                for insight in insights[:5]:
                    response += f"• {insight}\n"

            response += f"\n\n⏰ Анализ выполнен: {datetime.now().strftime('%d.%m.%Y %H:%M')}"

            buttons = [
                [
                    Button.inline('🔄 Новый анализ', b'category_self_analysis'),
                    Button.inline('📋 Другой чат', b'select_chat')
                ]
            ]

            await event.respond(response, buttons=buttons, parse_mode='markdown')

        except Exception as e:
            logger.error(f"Ошибка отправки результата: {e}")
            await event.respond(f"✅ Анализ завершен, но возникла ошибка форматирования: {str(e)}")

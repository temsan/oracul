"""Генерация меню и кнопок Telegram"""

from telethon import Button


class MenuMixin:
    """Миксин для генерации меню бота"""

    def get_main_menu(self):
        """Главное меню с категориями анализа"""
        buttons = []

        for category_id, category_data in self.analysis_categories.items():
            buttons.append([Button.inline(
                category_data['name'],
                f'category_{category_id}'.encode()
            )])

        buttons.extend([
            [
                Button.inline('📈 История анализов', b'history'),
                Button.inline('⚙️ Настройки', b'settings')
            ],
            [
                Button.inline('🔐 Сессия', b'session_settings'),
                Button.inline('🧩 Web App', b'open_webapp')
            ],
            [Button.inline('ℹ️ Помощь', b'help')]
        ])

        return buttons

    def get_self_analysis_menu(self):
        """Меню самоанализа диалогов"""
        return [
            [Button.inline('💬 Выбрать чат для анализа', b'select_chat')],
            [
                Button.inline('🔍 Быстрый анализ', b'quick_analysis'),
                Button.inline('📈 Глубокий анализ', b'deep_analysis')
            ],
            [
                Button.inline('🎤 Только голосовые', b'voice_only'),
                Button.inline('📝 Только текст', b'text_only')
            ],
            [Button.inline('🌍 Глобальный анализ', b'global_analysis')],
            [
                Button.inline('📅 За последний месяц', b'last_month'),
                Button.inline('📆 За последнюю неделю', b'last_week')
            ],
            [Button.inline('◀️ Назад', b'back_to_main')]
        ]

    def get_psychological_menu(self):
        """Меню психологического анализа"""
        buttons = []

        main_analyzers = ['big_five', 'hero_journey', 'psychological_types']
        for analyzer_id in main_analyzers:
            description = self.psychological_analyzers[analyzer_id]
            buttons.append([Button.inline(description, f'psych_{analyzer_id}'.encode())])

        buttons.append([Button.inline('🔬 Продвинутые анализы', b'advanced_psych')])

        buttons.extend([
            [Button.inline('💔 Анализ токсичных отношений', b'psych_toxic_relationships')],
            [Button.inline('💕 Стили привязанности', b'psych_attachment_styles')],
            [Button.inline('🌑 Работа с Тенью', b'psych_shadow_work')],
            [Button.inline('💭 Анализ запроса/проблемы', b'psych_problem_analysis')],
            [Button.inline('◀️ Назад', b'back_to_main')]
        ])

        return buttons

    def get_voice_analysis_menu(self):
        """Меню анализа голосовых"""
        return [
            [Button.inline('📅 Анализ по периодам', b'voice_periods')],
            [Button.inline('🎯 Анализ по фокусу', b'voice_focus')],
            [Button.inline('👤 Анализ по пользователям', b'voice_users')],
            [
                Button.inline('😊 Эмоциональное состояние', b'voice_emotions'),
                Button.inline('💬 Динамика отношений', b'voice_relationships')
            ],
            [Button.inline('🔍 Общие паттерны', b'voice_patterns')],
            [Button.inline('◀️ Назад', b'back_to_main')]
        ]

    def get_career_menu(self):
        """Меню карьерного анализа"""
        return [
            [Button.inline('🔍 Поиск вакансий', b'career_search')],
            [Button.inline('📝 Оптимизация резюме', b'career_resume')],
            [Button.inline('🤝 Нетворкинг', b'career_networking')],
            [Button.inline('📊 Анализ рынка', b'career_market')],
            [Button.inline('💰 Зарплатная аналитика', b'career_salary')],
            [Button.inline('◀️ Назад', b'back_to_main')]
        ]

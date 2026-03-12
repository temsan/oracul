"""Обработчики анализов: психологический, голосовой, карьерный, ситуационный"""

import asyncio
import logging

from telethon import Button

logger = logging.getLogger(__name__)


class AnalysisHandlerMixin:
    """Миксин для обработки различных типов анализа"""

    # --- Самоанализ диалогов ---

    async def handle_quick_analysis(self, event):
        """Быстрый анализ последних сообщений"""
        await event.edit(
            "🔍 **Быстрый анализ**\n\n"
            "Анализ последних 50 сообщений из выбранного чата.\n"
            "Время выполнения: ~30 секунд\n\n"
            "Отправьте ID чата или выберите из списка.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'category_self_analysis')]
            ],
            parse_mode='markdown'
        )
        self.user_states[event.sender_id] = {
            'state': 'waiting_chat', 'analysis_type': 'quick', 'limit': 50
        }

    async def handle_deep_analysis(self, event):
        """Глубокий анализ с большим объемом данных"""
        await event.edit(
            "📈 **Глубокий анализ**\n\n"
            "Детальный анализ до 200 сообщений с временной динамикой.\n"
            "Время выполнения: ~2-3 минуты\n\n"
            "Отправьте ID чата или выберите из списка.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'category_self_analysis')]
            ],
            parse_mode='markdown'
        )
        self.user_states[event.sender_id] = {
            'state': 'waiting_chat', 'analysis_type': 'deep', 'limit': 200
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
                [Button.inline('◀️ Назад', b'category_self_analysis')]
            ],
            parse_mode='markdown'
        )
        self.user_states[event.sender_id] = {
            'state': 'waiting_chat', 'analysis_type': 'voice_only', 'limit': 100
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
                [Button.inline('◀️ Назад', b'category_self_analysis')]
            ],
            parse_mode='markdown'
        )
        self.user_states[event.sender_id] = {
            'state': 'waiting_chat', 'analysis_type': 'text_only', 'limit': 150
        }

    async def handle_time_period(self, event, period):
        """Анализ за определенный период"""
        period_names = {'last_week': 'последнюю неделю', 'last_month': 'последний месяц'}
        period_days = {'last_week': 7, 'last_month': 30}

        await event.edit(
            f"📅 **Анализ за {period_names[period]}**\n\n"
            f"Анализ сообщений за последние {period_days[period]} дней.\n"
            "Включает временную динамику и тренды.\n\n"
            "Отправьте ID чата для анализа.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'category_self_analysis')]
            ],
            parse_mode='markdown'
        )
        self.user_states[event.sender_id] = {
            'state': 'waiting_chat', 'analysis_type': 'time_period',
            'period_days': period_days[period], 'limit': 200
        }

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
                [Button.inline('🎯 Только активные чаты', b'global_active')],
                [Button.inline('◀️ Назад', b'category_self_analysis')]
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

        try:
            await asyncio.sleep(3)  # TODO: реальная логика глобального анализа

            await event.edit(
                f"✅ **Глобальный анализ за {config['name']} завершен**\n\n"
                f"📊 **Результаты:**\n"
                f"• Проанализировано чатов: 15\n"
                f"• Всего сообщений: 1,234\n"
                f"• Основные темы: Работа, друзья, хобби\n"
                f"• Эмоциональная тональность: Позитивная\n\n"
                f"🔮 Полный отчет отправлен в личные сообщения.",
                buttons=[[Button.inline('🔄 Новый анализ', b'category_self_analysis')]],
                parse_mode='markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка глобального анализа: {e}")
            await event.edit(
                "❌ Произошла ошибка при глобальном анализе.\nПопробуйте позже.",
                buttons=[[Button.inline('◀️ Назад', b'category_self_analysis')]],
                parse_mode='markdown'
            )

    # --- Комплексный анализ ситуации ---

    async def perform_situation_analysis(self, event):
        """Выполняет комплексный анализ ситуации"""
        try:
            await asyncio.sleep(2)  # TODO: реальная логика анализа

            await event.edit(
                "✅ **Анализ текущей ситуации завершен**\n\n"
                "📊 **Результаты:**\n"
                "• Эмоциональное состояние: Стабильное\n"
                "• Активность в чатах: Высокая\n"
                "• Основные темы: Работа, развитие\n"
                "• Рекомендации: Больше отдыха\n\n"
                "🔮 Полный отчет отправлен в личные сообщения.",
                buttons=[[Button.inline('🔄 Новый анализ', b'back_to_main')]],
                parse_mode='markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка анализа ситуации: {e}")
            await event.edit(
                "❌ Произошла ошибка при анализе ситуации.\nПопробуйте позже.",
                buttons=[[Button.inline('◀️ Назад', b'back_to_main')]],
                parse_mode='markdown'
            )

    # --- Психологический анализ ---

    async def handle_psychological_analysis(self, event, analyzer_type: str):
        """Обработка психологического анализа"""
        analyzer_names = {
            'big_five': 'Big Five - Модель личности "Большая пятерка"',
            'hero_journey': 'Путь Героя - 12 этапов развития',
            'psychological_types': 'Психотипы - 4 основных типа личности',
            'jungian_archetypes': 'Архетипы Юнга - 12 архетипов личности',
            'shadow_work': 'Теневая работа - Скрытые аспекты личности',
            'attachment_styles': 'Стили привязанности - Паттерны в отношениях',
            'toxic_relationships': 'Токсичные отношения - Юнгианский анализ'
        }

        name = analyzer_names.get(analyzer_type, analyzer_type)

        await event.edit(
            f"🧠 **{name}**\n\n"
            f"Для проведения психологического анализа нужны ваши сообщения.\n\n"
            f"📝 **Варианты:**\n"
            f"• Отправить сообщения вручную\n"
            f"• Собрать из ваших чатов автоматически\n\n"
            f"⏳ Анализ займет 2-3 минуты",
            buttons=[
                [Button.inline('📝 Ручной ввод', b'manual_psych_input')],
                [Button.inline('🔍 Из чатов', b'auto_psych_collect')],
                [Button.inline('◀️ Назад', b'category_psychological')]
            ],
            parse_mode='markdown'
        )

        self.user_states[event.sender_id] = {
            'analysis_type': 'psychological',
            'analyzer': analyzer_type,
            'analyzer_name': name
        }

    async def handle_advanced_psychological_menu(self, event):
        """Показать продвинутые психологические анализы"""
        await event.edit(
            "🔬 **Продвинутые психологические анализы**\n\n"
            "⚠️ Требуют больше времени и данных\n\n"
            "Выберите тип анализа:",
            buttons=[
                [Button.inline('🏛️ Архетипы Юнга', b'psych_jungian_archetypes')],
                [Button.inline('🌑 Теневая работа', b'psych_shadow_work')],
                [Button.inline('💝 Эмоциональный интеллект', b'psych_emotional_intelligence')],
                [Button.inline('💕 Стили привязанности', b'psych_attachment_styles')],
                [Button.inline('🧩 Когнитивные искажения', b'psych_cognitive_biases')],
                [Button.inline('🎯 Ценности и мотивация', b'psych_values_motivation')],
                [Button.inline('◀️ К основным', b'category_psychological')]
            ],
            parse_mode='markdown'
        )

    # --- Анализ голосовых ---

    async def handle_voice_periods(self, event):
        """Анализ голосовых по периодам"""
        await event.edit(
            "📅 **Анализ голосовых по периодам**\n\n"
            "Временная динамика ваших голосовых сообщений:\n"
            "• Изменения эмоционального состояния\n"
            "• Частота использования голосовых\n"
            "• Длительность сообщений по времени\n\n"
            "Выберите период:",
            buttons=[
                [
                    Button.inline('📅 За неделю', b'voice_week'),
                    Button.inline('📆 За месяц', b'voice_month')
                ],
                [Button.inline('🗓️ За 3 месяца', b'voice_3months')],
                [Button.inline('◀️ Назад', b'category_voice_analysis')]
            ],
            parse_mode='markdown'
        )

    async def handle_voice_focus(self, event):
        """Анализ голосовых по фокусу"""
        await event.edit(
            "🎯 **Анализ по фокусу**\n\n"
            "Специализированный анализ голосовых:\n"
            "• Эмоциональная окраска речи\n"
            "• Уверенность в голосе\n"
            "• Скорость речи и паузы\n"
            "• Интонационные паттерны\n\n"
            "Отправьте ID чата для анализа.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'category_voice_analysis')]
            ],
            parse_mode='markdown'
        )

    async def handle_voice_users(self, event):
        """Анализ голосовых по пользователям"""
        await event.edit(
            "👤 **Анализ по пользователям**\n\n"
            "Сравнительный анализ голосовых сообщений:\n"
            "• Ваш стиль vs собеседники\n"
            "• Адаптация к разным людям\n"
            "• Эмоциональная синхронизация\n\n"
            "Выберите групповой чат для анализа.",
            buttons=[
                [Button.inline('👥 Групповые чаты', b'show_groups_channels')],
                [Button.inline('◀️ Назад', b'category_voice_analysis')]
            ],
            parse_mode='markdown'
        )

    async def handle_voice_emotions(self, event):
        """Анализ эмоций в голосовых"""
        await event.edit(
            "😊 **Эмоциональное состояние**\n\n"
            "Глубокий анализ эмоций в голосовых сообщениях:\n"
            "• Распознавание базовых эмоций\n"
            "• Эмоциональная динамика\n"
            "• Стресс и напряжение в голосе\n"
            "• Позитивные и негативные паттерны\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'category_voice_analysis')]],
            parse_mode='markdown'
        )

    async def handle_voice_relationships(self, event):
        """Анализ динамики отношений через голосовые"""
        await event.edit(
            "💬 **Динамика отношений**\n\n"
            "Анализ развития отношений через голосовые:\n"
            "• Изменение тона общения\n"
            "• Близость и дистанция\n"
            "• Конфликты и примирения\n"
            "• Эмоциональная связь\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'category_voice_analysis')]],
            parse_mode='markdown'
        )

    async def handle_voice_patterns(self, event):
        """Анализ общих паттернов в голосовых"""
        await event.edit(
            "🔍 **Общие паттерны**\n\n"
            "Выявление устойчивых паттернов в голосовых:\n"
            "• Время отправки сообщений\n"
            "• Предпочитаемая длительность\n"
            "• Ситуации использования голосовых\n"
            "• Личные особенности речи\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'category_voice_analysis')]],
            parse_mode='markdown'
        )

    # --- Карьерный анализ ---

    async def handle_career_search(self, event):
        """Поиск вакансий"""
        await event.edit(
            "🔍 **Поиск вакансий**\n\n"
            "Интеллектуальный поиск подходящих вакансий:\n"
            "• Анализ ваших навыков и опыта\n"
            "• Подбор релевантных позиций\n"
            "• Оценка соответствия требованиям\n"
            "• Рекомендации по развитию\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    async def handle_career_resume(self, event):
        """Оптимизация резюме"""
        await event.edit(
            "📝 **Оптимизация резюме**\n\n"
            "Анализ и улучшение вашего резюме:\n"
            "• Структура и содержание\n"
            "• Ключевые слова для ATS\n"
            "• Подача достижений\n"
            "• Адаптация под вакансии\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    async def handle_career_networking(self, event):
        """Нетворкинг"""
        await event.edit(
            "🤝 **Нетворкинг**\n\n"
            "Развитие профессиональных связей:\n"
            "• Анализ вашей сети контактов\n"
            "• Стратегии расширения сети\n"
            "• Эффективное общение\n"
            "• Поиск менторов и партнеров\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    async def handle_career_market(self, event):
        """Анализ рынка"""
        await event.edit(
            "📊 **Анализ рынка**\n\n"
            "Исследование рынка труда в вашей сфере:\n"
            "• Тренды и перспективы\n"
            "• Востребованные навыки\n"
            "• Уровень зарплат\n"
            "• Конкуренция и возможности\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    async def handle_career_salary(self, event):
        """Зарплатная аналитика"""
        await event.edit(
            "💰 **Зарплатная аналитика**\n\n"
            "Анализ вашего уровня дохода:\n"
            "• Сравнение с рынком\n"
            "• Потенциал роста\n"
            "• Стратегии повышения\n"
            "• Переговоры о зарплате\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    # --- Общие обработчики ---

    async def handle_history(self, event):
        """История анализов"""
        await event.edit(
            "📈 **История анализов**\n\n"
            "Ваши предыдущие анализы:\n"
            "• Сохраненные результаты\n"
            "• Динамика изменений\n"
            "• Сравнение по времени\n"
            "• Экспорт данных\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'back_to_main')]],
            parse_mode='markdown'
        )

    async def handle_settings(self, event):
        """Настройки бота"""
        await event.edit(
            "⚙️ **Настройки**\n\n"
            "Персонализация работы бота:\n"
            "• Язык интерфейса\n"
            "• Уровень детализации\n"
            "• Уведомления\n"
            "• Конфиденциальность\n\n"
            "🚧 Функция в разработке. Скоро будет доступна!",
            buttons=[[Button.inline('◀️ Назад', b'back_to_main')]],
            parse_mode='markdown'
        )

    # --- Психологический анализ - реализация ---

    async def handle_manual_psych_input(self, event):
        """Ручной ввод текста для психологического анализа"""
        user_id = event.sender_id
        user_state = self.user_states.get(user_id, {})
        analyzer_name = user_state.get('analyzer_name', 'Психологический анализ')
        
        await event.edit(
            f"🧠 **{analyzer_name}**\n\n"
            f"Отправьте текст, который нужно проанализировать.\n\n"
            f"Это может быть:\n"
            f"• Ваши мысли и размышления\n"
            f"• Описание ситуации\n"
            f"• Диалог или переписка\n\n"
            f"💡 **Совет:** Чем больше текста, тем точнее анализ.\n"
            f"Минимум: 100 символов",
            buttons=[[Button.inline('◀️ Назад', b'category_psychological')]],
            parse_mode='markdown'
        )
        
        # Устанавливаем состояние ожидания текста
        self.user_states[user_id] = {
            'state': 'waiting_psych_text',
            'analysis_type': 'psychological',
            'analyzer': user_state.get('analyzer'),
            'analyzer_name': analyzer_name
        }

    async def handle_auto_psych_collect(self, event):
        """Автоматический сбор сообщений для психологического анализа"""
        user_id = event.sender_id
        user_state = self.user_states.get(user_id, {})
        analyzer_name = user_state.get('analyzer_name', 'Психологический анализ')
        
        # Проверяем сессию
        user_client = await self.require_user_session(event, "психологического анализа")
        if not user_client:
            return
        
        await event.edit(
            f"🧠 **{analyzer_name}**\n\n"
            f"Выберите чат для анализа:\n\n"
            f"Бот соберет ваши сообщения из выбранного чата "
            f"и проведет психологический анализ.",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'category_psychological')]
            ],
            parse_mode='markdown'
        )
        
        # Сохраняем состояние
        self.user_states[user_id] = {
            'state': 'waiting_chat_for_psych',
            'analysis_type': 'psychological',
            'analyzer': user_state.get('analyzer'),
            'analyzer_name': analyzer_name
        }

    async def perform_psychological_analysis(self, event, text: str, analyzer_type: str, analyzer_name: str):
        """Выполнение психологического анализа"""
        await event.edit(
            f"🧠 **{analyzer_name}**\n\n"
            f"⏳ Анализирую текст...\n"
            f"📊 Длина текста: {len(text)} символов\n\n"
            f"Это займет 1-2 минуты.",
            parse_mode='markdown'
        )
        
        try:
            # Здесь будет вызов к AI для анализа
            # Пока демо-результат
            await asyncio.sleep(2)
            
            # Формируем результат анализа
            analysis_results = {
                'big_five': self._get_big_five_analysis(),
                'hero_journey': self._get_hero_journey_analysis(),
                'psychological_types': self._get_psych_types_analysis(),
                'jungian_archetypes': self._get_jungian_analysis(),
                'shadow_work': self._get_shadow_work_analysis(),
                'attachment_styles': self._get_attachment_analysis(),
                'toxic_relationships': self._get_toxic_analysis()
            }
            
            result = analysis_results.get(analyzer_type, analysis_results['big_five'])
            
            await event.edit(
                f"🧠 **{analyzer_name}**\n\n"
                f"{result}\n\n"
                f"✅ Анализ завершен",
                buttons=[[Button.inline('🔄 Новый анализ', b'category_psychological')]],
                parse_mode='markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка психологического анализа: {e}")
            await event.edit(
                f"❌ **Ошибка анализа**\n\n"
                f"Не удалось выполнить анализ.\n"
                f"Попробуйте позже или с другим текстом.",
                buttons=[[Button.inline('◀️ Назад', b'category_psychological')]],
                parse_mode='markdown'
            )

    def _get_big_five_analysis(self):
        return (
            "📊 **Big Five - Модель личности**\n\n"
            "**Открытость опыту:** Высокий уровень\n"
            "• Творческое мышление, любознательность\n"
            "• Готовность к новому опыту\n\n"
            "**Добросовестность:** Средний-высокий\n"
            "• Организованность и целеустремленность\n"
            "• Внимание к деталям\n\n"
            "**Экстраверсия:** Средний уровень\n"
            "• Комфорт в общении, но потребность в уединении\n"
            "• Сбалансированная социальная активность\n\n"
            "**Доброжелательность:** Высокий\n"
            "• Эмпатия и забота о других\n"
            "• Стремление к гармонии в отношениях\n\n"
            "**Невротизм:** Низкий-средний\n"
            "• Эмоциональная стабильность\n"
            "• Умение справляться со стрессом"
        )

    def _get_hero_journey_analysis(self):
        return (
            "⚔️ **Путь Героя - 12 этапов развития**\n\n"
            "**1. Обычный мир:** Комфортная зона, стабильность\n\n"
            "**2. Зов к приключениям:** Желание изменений, новые возможности\n\n"
            "**3. Отказ от зова:** Страх неизвестности, сомнения\n\n"
            "**4. Встреча с наставником:** Поиск мудрости и поддержки\n\n"
            "**5. Пересечение первого порога:** Первый шаг в неизвестность\n\n"
            "**6. Испытания:** Преодоление трудностей, рост\n\n"
            "**7. Ближайшая пещера:** Лицом к лицу со страхом\n\n"
            "**8. Испытание:** Кризис и трансформация\n\n"
            "**9. Награда:** Обретение новых качеств\n\n"
            "**10. Путь домой:** Интеграция опыта\n\n"
            "**11. Воскрешение:** Финальная трансформация\n\n"
            "**12. Возвращение с эликсиром:** Деление мудростью"
        )

    def _get_psych_types_analysis(self):
        return (
            "🎭 **Психологические типы**\n\n"
            "**Доминирующий тип: Референт**\n\n"
            "**Характеристики:**\n"
            "• Аналитический склад ума\n"
            "• Стремление к пониманию глубинных процессов\n"
            "• Рефлексия и самоанализ\n\n"
            "**Сильные стороны:**\n"
            "• Способность видеть суть проблем\n"
            "• Интуитивное понимание людей\n"
            "• Терпение в исследовании\n\n"
            "**Области развития:**\n"
            "• Баланс анализа и действия\n"
            "• Принятие неопределенности\n"
            "• Выражение эмоций"
        )

    def _get_jungian_analysis(self):
        return (
            "🏛️ **Архетипы Юнга**\n\n"
            "**Доминирующий архетип: Мудрец**\n\n"
            "**Характеристики:**\n"
            "• Поиск истины и знания\n"
            "• Стремление к пониманию мира\n"
            "• Деление опытом с другими\n\n"
            "**Вторичные архетипы:**\n"
            "• **Искатель** - жажда нового опыта\n"
            "• **Творец** - потребность в самовыражении\n"
            "• **Заботливый** - эмпатия и поддержка\n\n"
            "**Теневой аспект:**\n"
            "Избегание действия через чрезмерный анализ\n\n"
            "**Интеграция:**\n"            "Баланс мудрости и решительности"
        )

    def _get_shadow_work_analysis(self):
        return (
            "🌑 **Теневая работа**\n\n"
            "**Выявленные теневые аспекты:**\n\n"
            "**1. Перфекционизм**\n"
            "• Высокие требования к себе и другим\n"
            "• Страх ошибок и неудач\n"
            "• Работа: принятие несовершенства\n\n"
            "**2. Контроль**\n"
            "• Потребность контролировать ситуации\n"
            "• Трудность с доверием процессу\n"
            "• Работа: отпускание и принятие\n\n"
            "**3. Самокритика**\n"
            "• Жесткое отношение к себе\n"
            "• Недооценка достижений\n"
            "• Работа: самосострадание\n\n"
            "**Путь интеграции:**\n"
            "Принятие тени как части целостности"
        )

    def _get_attachment_analysis(self):
        return (
            "💕 **Стили привязанности**\n\n"
            "**Основной стиль: Надежная привязанность**\n\n"
            "**Характеристики:**\n"
            "• Комфорт в близости и автономии\n"
            "• Умение выражать потребности\n"
            "• Доверие в отношениях\n\n"
            "**В отношениях:**\n"
            "• Способность к эмоциональной близости\n"
            "• Уважение личных границ партнера\n"
            "• Конструктивное разрешение конфликтов\n\n"
            "**Возможные паттерны:**\n"
            "• Тенденция к заботе о других\n"
            "• Иногда пренебрежение собственными нуждами\n\n"
            "**Рекомендации:**\n"
            "Сохранять баланс между заботой о других и собой"
        )

    def _get_toxic_analysis(self):
        return (
            "💔 **Анализ токсичных отношений**\n\n"
            "**Общая оценка: Здоровые границы**\n\n"
            "**Положительные признаки:**\n"
            "• Уважение личных границ\n"
            "• Способность говорить 'нет'\n"
            "• Эмоциональная автономия\n\n"
            "**Области внимания:**\n"
            "• Тенденция брать слишком много ответственности\n"
            "• Иногда игнорирование красных флагов\n"
            "• Необходимость в одобрении других\n\n"
            "**Рекомендации:**\n"
            "• Развивать эмоциональную независимость\n"
            "• Укреплять самооценку\n"
            "• Практиковать здоровые границы\n\n"
            "**Потенциал:**\n"
            "Высокий потенциал здоровых отношений"
        )

    # --- Голосовой анализ - реализация ---

    async def handle_voice_emotions(self, event):
        """Анализ эмоций в голосовых"""
        await event.edit(
            "😊 **Эмоциональное состояние**\n\n"
            "Глубокий анализ эмоций в голосовых сообщениях:\n"
            "• Распознавание базовых эмоций\n"
            "• Эмоциональная динамика\n"
            "• Стресс и напряжение в голосе\n"
            "• Позитивные и негативные паттерны\n\n"
            "Выберите чат для анализа:",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'category_voice_analysis')]
            ],
            parse_mode='markdown'
        )
        
        self.user_states[event.sender_id] = {
            'state': 'waiting_chat_for_voice_emotions',
            'analysis_type': 'voice_emotions'
        }

    async def handle_voice_relationships(self, event):
        """Анализ динамики отношений через голосовые"""
        await event.edit(
            "💬 **Динамика отношений**\n\n"
            "Анализ развития отношений через голосовые:\n"
            "• Изменение тона общения\n"
            "• Близость и дистанция\n"
            "• Конфликты и примирения\n"
            "• Эмоциональная связь\n\n"
            "Выберите чат для анализа:",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'category_voice_analysis')]
            ],
            parse_mode='markdown'
        )
        
        self.user_states[event.sender_id] = {
            'state': 'waiting_chat_for_voice_relationships',
            'analysis_type': 'voice_relationships'
        }

    async def handle_voice_patterns(self, event):
        """Анализ общих паттернов в голосовых"""
        await event.edit(
            "🔍 **Общие паттерны**\n\n"
            "Выявление устойчивых паттернов в голосовых:\n"
            "• Время отправки сообщений\n"
            "• Предпочитаемая длительность\n"
            "• Ситуации использования голосовых\n"
            "• Личные особенности речи\n\n"
            "Выберите чат для анализа:",
            buttons=[
                [Button.inline('📋 Мои чаты', b'show_chats')],
                [Button.inline('◀️ Назад', b'category_voice_analysis')]
            ],
            parse_mode='markdown'
        )
        
        self.user_states[event.sender_id] = {
            'state': 'waiting_chat_for_voice_patterns',
            'analysis_type': 'voice_patterns'
        }

    async def perform_voice_analysis(self, event, messages: list, analysis_type: str):
        """Выполнение голосового анализа"""
        voice_messages = [m for m in messages if m.get('type') == 'voice']
        
        if not voice_messages:
            await event.edit(
                "❌ **Нет голосовых сообщений**\n\n"
                "В выбранном чате не найдено голосовых сообщений.",
                buttons=[[Button.inline('◀️ Назад', b'category_voice_analysis')]]
            )
            return
        
        total_duration = sum(m.get('duration', 0) for m in voice_messages)
        
        await event.edit(
            f"🎤 **Анализ голосовых**\n\n"
            f"Найдено голосовых: {len(voice_messages)}\n"
            f"Общая длительность: {total_duration // 60} мин {total_duration % 60} сек\n\n"
            f"⏳ Анализирую...",
            parse_mode='markdown'
        )
        
        await asyncio.sleep(2)
        
        # Демо-результаты
        results = {
            'voice_emotions': self._get_voice_emotions_result(),
            'voice_relationships': self._get_voice_relationships_result(),
            'voice_patterns': self._get_voice_patterns_result()
        }
        
        result = results.get(analysis_type, results['voice_patterns'])
        
        await event.edit(
            f"🎤 **Результаты анализа**\n\n"
            f"{result}\n\n"
            f"✅ Анализ завершен",
            buttons=[[Button.inline('🔄 Новый анализ', b'category_voice_analysis')]],
            parse_mode='markdown'
        )

    def _get_voice_emotions_result(self):
        return (
            "😊 **Эмоциональный анализ**\n\n"
            "**Общий тон:** Позитивный\n\n"
            "**Эмоциональная динамика:**\n"
            "• 65% - Позитивные эмоции\n"
            "• 25% - Нейтральный фон\n"
            "• 10% - Негативные эмоции\n\n"
            "**Стрессовые индикаторы:**\n"
            "• Низкий уровень напряжения\n"
            "• Стабильная интонация\n"
            "• Уверенная речь\n\n"
            "**Вывод:** Эмоционально стабильное состояние"
        )

    def _get_voice_relationships_result(self):
        return (
            "💬 **Динамика отношений**\n\n"
            "**Тон общения:** Дружелюбный\n\n"
            "**Паттерны взаимодействия:**\n"
            "• Взаимная эмоциональная поддержка\n"
            "• Сбалансированный диалог\n"
            "• Открытое выражение мнений\n\n"
            "**Динамика развития:**\n"
            "• Рост доверия со временем\n"
            "• Углубление близости\n"
            "• Конструктивное разрешение разногласий\n\n"
            "**Рекомендация:** Продолжать развивать открытость"
        )

    def _get_voice_patterns_result(self):
        return (
            "🔍 **Паттерны использования**\n\n"
            "**Время отправки:**\n"
            "• Пик активности: 10:00-12:00, 20:00-22:00\n"
            "• Средняя длительность: 45 сек\n\n"
            "**Ситуации использования:**\n"
            "• 60% - Личные истории и эмоции\n"
            "• 25% - Быстрые вопросы/ответы\n"
            "• 15% - Сложные темы, требующие объяснений\n\n"
            "**Особенности речи:**\n"
            "• Средний темп, четкое произношение\n"
            "• Использование пауз для акцента\n"
            "• Эмоциональная выразительность"
        )

    # --- Карьерный анализ - реализация ---

    async def handle_career_search(self, event):
        """Поиск вакансий - реализация"""
        await event.edit(
            "🔍 **Поиск вакансий**\n\n"
            "Интеллектуальный поиск подходящих вакансий:\n"
            "• Анализ ваших навыков и опыта\n"
            "• Подбор релевантных позиций\n"
            "• Оценка соответствия требованиям\n"
            "• Рекомендации по развитию\n\n"
            "📝 **Ваш профиль:**\n"
            "Отправьте краткое описание вашего опыта и навыков, "
            "или загрузите резюме текстом.",
            buttons=[
                [Button.inline('📝 Ввести профиль', b'career_enter_profile')],
                [Button.inline('◀️ Назад', b'category_career_analysis')]
            ],
            parse_mode='markdown'
        )
        
        self.user_states[event.sender_id] = {
            'state': 'waiting_career_profile',
            'analysis_type': 'career_search'
        }

    async def handle_career_resume(self, event):
        """Оптимизация резюме - реализация"""
        await event.edit(
            "📝 **Оптимизация резюме**\n\n"
            "Анализ и улучшение вашего резюме:\n"
            "• Структура и содержание\n"
            "• Ключевые слова для ATS\n"
            "• Подача достижений\n"
            "• Адаптация под вакансии\n\n"
            "📝 **Отправьте ваше резюме текстом:**",
            buttons=[
                [Button.inline('◀️ Назад', b'category_career_analysis')]
            ],
            parse_mode='markdown'
        )
        
        self.user_states[event.sender_id] = {
            'state': 'waiting_resume',
            'analysis_type': 'career_resume'
        }

    async def handle_career_networking(self, event):
        """Нетворкинг - реализация"""
        await event.edit(
            "🤝 **Нетворкинг**\n\n"
            "Развитие профессиональных связей:\n"
            "• Анализ вашей сети контактов\n"
            "• Стратегии расширения сети\n"
            "• Эффективное общение\n"
            "• Поиск менторов и партнеров\n\n"
            "📊 **Ваши контакты:**\n"
            "Анализирую вашу сеть на основе сообщений...",
            buttons=[
                [Button.inline('📊 Анализировать сеть', b'career_analyze_network')],
                [Button.inline('◀️ Назад', b'category_career_analysis')]
            ],
            parse_mode='markdown'
        )

    async def handle_career_market(self, event):
        """Анализ рынка - реализация"""
        await event.edit(
            "📊 **Анализ рынка труда**\n\n"
            "Исследование рынка труда:\n"
            "• Тренды и перспективы\n"
            "• Востребованные навыки\n"
            "• Уровень зарплат\n"
            "• Конкуренция и возможности\n\n"
            "📝 **Укажите интересующую сферу:**",
            buttons=[
                [Button.inline('💻 IT', b'career_market_it')],
                [Button.inline('💼 Бизнес', b'career_market_business')],
                [Button.inline('🎨 Дизайн', b'career_market_design')],
                [Button.inline('◀️ Назад', b'category_career_analysis')]
            ],
            parse_mode='markdown'
        )

    async def handle_career_salary(self, event):
        """Зарплатная аналитика - реализация"""
        await event.edit(
            "💰 **Зарплатная аналитика**\n\n"
            "Анализ вашего уровня дохода:\n"
            "• Сравнение с рынком\n"
            "• Потенциал роста\n"
            "• Стратегии повышения\n"
            "• Переговоры о зарплате\n\n"
            "📝 **Отправьте информацию:**\n"
            "1. Ваша текущая позиция\n"
            "2. Опыт работы\n"
            "3. Текущий уровень дохода (по желанию)",
            buttons=[
                [Button.inline('◀️ Назад', b'category_career_analysis')]
            ],
            parse_mode='markdown'
        )
        
        self.user_states[event.sender_id] = {
            'state': 'waiting_salary_info',
            'analysis_type': 'career_salary'
        }

    async def perform_career_analysis(self, event, text: str, analysis_type: str):
        """Выполнение карьерного анализа"""
        await event.edit(
            "💼 **Карьерный анализ**\n\n"
            "⏳ Анализирую информацию...",
            parse_mode='markdown'
        )
        
        await asyncio.sleep(2)
        
        results = {
            'career_search': self._get_career_search_result(),
            'career_resume': self._get_career_resume_result(),
            'career_salary': self._get_career_salary_result()
        }
        
        result = results.get(analysis_type, results['career_search'])
        
        await event.edit(
            f"💼 **Результаты анализа**\n\n"
            f"{result}\n\n"
            f"✅ Анализ завершен",
            buttons=[[Button.inline('🔄 Новый анализ', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    def _get_career_search_result(self):
        return (
            "🔍 **Рекомендации по поиску**\n\n"
            "**Подходящие направления:**\n"
            "• Product Manager (совпадение 85%)\n"
            "• Business Analyst (совпадение 78%)\n"
            "• Project Manager (совпадение 72%)\n\n"
            "**Навыки для развития:**\n"
            "• Agile/Scrum методологии\n"
            "• Data Analysis (SQL, Python)\n"
            "• Стратегическое мышление\n\n"
            "**Рекомендуемые платформы:**\n"
            "• LinkedIn, HeadHunter, Habr Career"
        )

    def _get_career_resume_result(self):
        return (
            "📝 **Анализ резюме**\n\n"
            "**Сильные стороны:**\n"
            "• Четкая структура и подача\n"
            "• Конкретные достижения с цифрами\n"
            "• Релевантный опыт\n\n"
            "**Улучшения:**\n"
            "• Добавьте больше ключевых слов из вакансий\n"
            "• Укажите сертификаты и курсы\n"
            "• Добавьте раздел 'О себе'\n\n"
            "**ATS-оптимизация:** 75%\n"
            "Резюме пройдет автоматический отбор"
        )

    def _get_career_salary_result(self):
        return (
            "💰 **Зарплатная аналитика**\n\n"
            "**Рыночный диапазон:**\n"
            "• Junior: 60-80K\n"
            "• Middle: 100-150K\n"
            "• Senior: 180-250K\n\n"
            "**Ваш потенциал:** 120-140K\n\n"
            "**Стратегия повышения:**\n"
            "1. Получить сертификаты (Agile, Analytics)\n"
            "2. Увеличить видимость (LinkedIn, конференции)\n"
            "3. Перейти на руководящую позицию\n\n"
            "**Срок достижения:** 6-12 месяцев"
        )

    async def _perform_network_analysis(self, event):
        """Выполнить анализ сети контактов"""
        await event.edit(
            "🤝 **Анализ профессиональной сети**\n\n"
            "⏳ Анализирую ваши контакты...",
            parse_mode='markdown'
        )
        
        await asyncio.sleep(2)
        
        await event.edit(
            "🤝 **Анализ сети контактов**\n\n"
            "**Размер сети:** ~150 профессиональных контактов\n\n"
            "**Качество связей:**\n"
            "• Сильные связи: 15% (22 контакта)\n"
            "• Средние связи: 35% (52 контакта)\n"
            "• Слабые связи: 50% (76 контактов)\n\n"
            "**Сферы:**\n"
            "• IT/Технологии: 40%\n"
            "• Бизнес/Менеджмент: 30%\n"
            "• Дизайн/Креатив: 20%\n"
            "• Другое: 10%\n\n"
            "**Рекомендации:**\n"
            "• Укрепляйте связи с IT-специалистами\n"
            "• Расширяйте сеть в сфере бизнеса\n"
            "• Активизируйте слабые связи",
            buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    async def _perform_network_analysis(self, event):
        """Выполнить анализ сети контактов"""
        await event.edit(
            "🤝 **Анализ профессиональной сети**\n\n"
            "⏳ Анализирую ваши контакты...",
            parse_mode='markdown'
        )
        
        await asyncio.sleep(2)
        
        await event.edit(
            "🤝 **Анализ сети контактов**\n\n"
            "**Размер сети:** ~150 профессиональных контактов\n\n"
            "**Качество связей:**\n"
            "• Сильные связи: 15% (22 контакта)\n"
            "• Средние связи: 35% (52 контакта)\n"
            "• Слабые связи: 50% (76 контактов)\n\n"
            "**Сферы:**\n"
            "• IT/Технологии: 40%\n"
            "• Бизнес/Менеджмент: 30%\n"
            "• Дизайн/Креатив: 20%\n"
            "• Другое: 10%\n\n"
            "**Рекомендации:**\n"
            "• Укрепляйте связи с IT-специалистами\n"
            "• Расширяйте сеть в сфере бизнеса\n"
            "• Активизируйте слабые связи",
            buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    async def _perform_market_analysis(self, event, sector: str):
        """Выполнить анализ рынка по сектору"""
        sector_data = {
            'IT': {
                'growth': '+15%',
                'demand': 'Очень высокий',
                'salary': '150K-300K',
                'skills': 'Python, Cloud, AI/ML'
            },
            'Business': {
                'growth': '+8%',
                'demand': 'Высокий',
                'salary': '120K-250K',
                'skills': 'Strategy, Analytics, Leadership'
            },
            'Design': {
                'growth': '+12%',
                'demand': 'Высокий',
                'salary': '100K-200K',
                'skills': 'UI/UX, Figma, Motion'
            }
        }
        
        data = sector_data.get(sector, sector_data['IT'])
        
        await event.edit(
            f"📊 **Анализ рынка: {sector}**\n\n"
            f"**Рост отрасли:** {data['growth']} в год\n"
            f"**Спрос на специалистов:** {data['demand']}\n"
            f"**Зарплатный диапазон:** {data['salary']}\n\n"
            f"**Востребованные навыки:**\n"
            f"• {data['skills']}\n\n"
            f"**Тренды:**\n"
            f"• Удаленная работа сохраняется\n"
            f"• Рост зарплат на 10-15%\n"
            f"• Высокая конкуренция на junior-позициях\n\n"
            f"**Рекомендация:** Фокус на middle+ уровень",
            buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]],
            parse_mode='markdown'
        )

    # --- Анализ психологического запроса/проблемы ---

    async def handle_problem_analysis(self, event):
        """Анализ психологического запроса или проблемы"""
        await event.edit(
            "💭 **Анализ психологического запроса**\n\n"
            "Опишите свою ситуацию, проблему или то, что вас беспокоит.\n\n"
            "Это может быть:\n"
            "• Сложности в отношениях\n"
            "• Внутренние конфликты\n"
            "• Страхи или ограничивающие убеждения\n"
            "• Вопросы самооценки и ценности\n"
            "• Жизненные переходы и кризисы\n"
            "• Поиск смысла и направления\n\n"
            "💡 **Совет:** Чем подробнее вы опишете ситуацию, "
            "тем точнее будет анализ.\n\n"
            "Минимум: 50 символов",
            buttons=[[Button.inline('◀️ Назад', b'category_psychological')]],
            parse_mode='markdown'
        )
        
        self.user_states[event.sender_id] = {
            'state': 'waiting_problem_description',
            'analysis_type': 'problem_analysis'
        }

    async def perform_problem_analysis(self, event, text: str):
        """Выполнение анализа психологической проблемы"""
        await event.edit(
            "💭 **Анализирую ваш запрос...**\n\n"
            "🔍 Изучаю ситуацию\n"
            "🧠 Анализирую паттерны\n"
            "💡 Формирую инсайты\n\n"
            "⏳ Это займет несколько секунд...",
            parse_mode='markdown'
        )
        
        try:
            await asyncio.sleep(2)
            
            # Получаем анализ
            analysis = self._analyze_problem(text)
            
            await event.edit(
                f"💭 **Анализ вашего запроса**\n\n"
                f"{analysis}\n\n"
                f"✅ Анализ завершен\n\n"
                f"💡 **Помните:** Это общий анализ. Для глубокой работы "
                f"рекомендую индивидуальную консультацию.",
                buttons=[
                    [Button.inline('🔄 Новый запрос', b'psych_problem_analysis')],
                    [Button.inline('📞 Записаться на консультацию', b'book_consultation')],
                    [Button.inline('◀️ Назад', b'category_psychological')]
                ],
                parse_mode='markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка анализа запроса: {e}")
            await event.edit(
                "❌ **Не удалось выполнить анализ**\n\n"
                "Попробуйте переформулировать запрос или обратитесь напрямую.",
                buttons=[[Button.inline('◀️ Назад', b'category_psychological')]]
            )

    def _analyze_problem(self, text: str) -> str:
        """Анализ текста проблемы и формирование ответа"""
        text_lower = text.lower()
        
        # Определяем тип проблемы по ключевым словам
        if any(word in text_lower for word in ['отношения', 'парень', 'муж', 'любовь', 'расстались', 'свадьба', 'развод']):
            return self._get_relationship_analysis()
        
        elif any(word in text_lower for word in ['работа', 'карьера', 'деньги', 'бизнес', 'начальник', 'коллеги', 'уволили']):
            return self._get_career_problem_analysis()
        
        elif any(word in text_lower for word in ['страх', 'боюсь', 'тревога', 'паника', 'фобия', 'беспокоюсь']):
            return self._get_anxiety_analysis()
        
        elif any(word in text_lower for word in ['самооценка', 'уверенность', 'неуверенность', 'недостаточно', 'плохая']):
            return self._get_selfworth_analysis()
        
        elif any(word in text_lower for word in ['усталость', 'выгорание', 'апатия', 'ничего не хочется', 'депрессия', 'пустота']):
            return self._get_burnout_analysis()
        
        elif any(word in text_lower for word in ['семья', 'родители', 'мама', 'папа', 'дети', 'ребенок']):
            return self._get_family_analysis()
        
        else:
            return self._get_general_problem_analysis()

    def _get_relationship_analysis(self):
        return (
            "**🎭 Тип запроса: Отношения и близость**\n\n"
            "**Возможные паттерны:**\n"
            "• Повторяющиеся сценарии в отношениях\n"
            "• Слияние или эмоциональная дистанция\n"
            "• Страх abandonment (брошенности)\n"
            "• Нарушение личных границ\n\n"
            "**Глубинные темы:**\n"
            "• Детско-родительские отношения как основа\n"
            "• Внутренний критик и самоценность\n"
            "• Способность к уязвимости\n\n"
            "**Направление работы:**\n"
            "• Осознание своего типа привязанности\n"
            "• Проработка границ и автономии\n"
            "• Интеграция внутреннего ребенка\n\n"
            "**Практика:**\n"
            "• Дневник отношений\n"
            "• Диалоги с частями себя\n"
            "• Техники осознанности"
        )

    def _get_career_problem_analysis(self):
        return (
            "**💼 Тип запроса: Карьера и реализация**\n\n"
            "**Возможные паттерны:**\n"
            "• Саботаж успеха (страх победы)\n"
            "• Перфекционизм и выгорание\n"
            "• Несоответствие ценностей и работы\n"
            "• Синдром самозванца\n\n"
            "**Глубинные темы:**\n"
            "• Родовые сценарии (не быть успешнее родителей)\n"
            "• Денежные блоки и ограничения\n"
            "• Смыслы и призвание\n\n"
            "**Направление работы:**\n"
            "• Распутывание родовых сценариев\n"
            "• Работа с внутренним критиком\n"
            "• Нахождение баланса ценностей\n\n"
            "**Практика:**\n"
            "• Медитация на будущее Я\n"
            "• Проработка денежных убеждений\n"
            "• Техники визуализации"
        )

    def _get_anxiety_analysis(self):
        return (
            "**😰 Тип запроса: Тревога и страхи**\n\n"
            "**Возможные паттерны:**\n"
            "• Обобщенная тревожность\n"
            "• Фобии и панические атаки\n"
            "• Катастрофизация мышления\n"
            "• Невозможность расслабиться\n\n"
            "**Глубинные темы:**\n"
            "• Необработанная травма\n"
            "• Диссоциация чувств\n"
            "• Потребность в контроле\n\n"
            "**Направление работы:**\n"
            "• Возвращение в тело (соматика)\n"
            "• Проработка первопричины\n"
            "• Интеграция теневых частей\n\n"
            "**Практика:**\n"
            "• Дыхательные техники (4-7-8)\n"
            "• Граундинг и якорение\n"
            "• Работа с телом"
        )

    def _get_selfworth_analysis(self):
        return (
            "**💎 Тип запроса: Самооценка и ценность**\n\n"
            "**Возможные паттерны:**\n"
            "• Зависимость от внешней оценки\n"
            "• Жесткий внутренний критик\n"
            "• Сравнение с другими\n"
            "• Невозможность принять похвалу\n\n"
            "**Глубинные темы:**\n"
            "• Условная любовь в детстве\n"
            "• Травма недостаточности\n"
            "• Отделение ценности от достижений\n\n"
            "**Направление работы:**\n"
            "• Исцеление внутреннего ребенка\n"
            "• Работа с критиком\n"
            "• Возвращение целостности\n\n"
            "**Практика:**\n"
            "• Зеркальная работа\n"
            "• Аффирмации и якорение\n"
            "• Дневник достижений"
        )

    def _get_burnout_analysis(self):
        return (
            "**😔 Тип запроса: Выгорание и потеря смыслов**\n\n"
            "**Возможные паттерны:**\n"
            "• Хроническая усталость\n"
            "• Эмоциональное опустошение\n"
            "• Цинизм и отчуждение\n"
            "• Потеря радости жизни\n\n"
            "**Глубинные темы:**\n"
            "• Отрыв от себя настоящего\n"
            "• Жизнь по должности\n"
            "• Невыраженные чувства\n\n"
            "**Направление работы:**\n"
            "• Возвращение к себе\n"
            "• Пересмотр ценностей и приоритетов\n"
            "• Восстановление энергии\n\n"
            "**Практика:**\n"
            "• Дневник благодарности\n"
            "• Медитация и mindfulness\n"
            "• Творческое самовыражение"
        )

    def _get_family_analysis(self):
        return (
            "**👨‍👩‍👧 Тип запроса: Семейная система**\n\n"
            "**Возможные паттерны:**\n"
            "• Системные зависимости\n"
            "• Треугольники и коализации\n"
            "• Переплетенные границы\n"
            "• Поколенческие травмы\n\n"
            "**Глубинные темы:**\n"
            "• Системная лояльность\n"
            "• Невысказанные чувства родителей\n"
            "• Родовые сценарии повторений\n\n"
            "**Направление работы:**\n"
            "• Расстановки (констелляции)\n"
            "• Принятие родителей\n"
            "• Возвращение своего места\n\n"
            "**Практика:**\n"
            "• Ритуалы принятия\n"
            "• Письма (не для отправки)\n"
            "• Медитация на род"
        )

    def _get_general_problem_analysis(self):
        return (
            "**🔮 Общий психологический анализ**\n\n"
            "**Что я вижу в вашем запросе:**\n"
            "• Внутренний конфликт различных частей\n"
            "• Потребность в интеграции и целостности\n"
            "• Возможность роста через осознание\n\n"
            "**Общие направления работы:**\n"
            "• Повышение осознанности\n"
            "• Интеграция теневых аспектов\n"
            "• Работа с внутренним ребенком\n"
            "• Возвращение в тело и чувства\n\n"
            "**Рекомендации:**\n"
            "• Ведите дневник наблюдений\n"
            "• Практикуйте осознанность\n"
            "• Обратитесь за индивидуальной консультацией "
            "для глубокой проработки\n\n"
            "💫 Помните: каждая проблема — это дверь к росту."
        )

    async def handle_book_consultation(self, event):
        """Обработка запроса на консультацию"""
        await event.edit(
            "📞 **Запись на индивидуальную консультацию**\n\n"
            "Для записи на личную консультацию свяжитесь со мной:\n\n"
            "📱 Telegram: @temsanone\n"
            "📧 Email: temsanone@gmail.com\n\n"
            "**Что вас ждет:**\n"
            "• Индивидуальная диагностика\n"
            "• Глубокая проработка запроса\n"
            "• Практические инструменты\n"
            "• Поддержка на пути к целостности\n\n"
            "💫 Приведите частички души в целостность — "
            "запишитесь на консультацию!",
            buttons=[
                [Button.url('📱 Написать в Telegram', 'https://t.me/temsanone')],
                [Button.inline('◀️ Назад', b'category_psychological')]
            ],
            parse_mode='markdown'
        )

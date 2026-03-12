#!/usr/bin/env python3
"""
Анализатор канала Абрамовой (1681841249) и связанной группы (1605750182)
Специализированный анализ для маркетингового канала с фокусом на рекламу в Telegram
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError
import re
from collections import Counter

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

class AbramovaChannelAnalyzer:
    def __init__(self):
        self.client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        self.marketing_keywords = [
            'реклама', 'маркетинг', 'продвижение', 'таргет', 'smm', 'контент',
            'бренд', 'продажи', 'воронка', 'лид', 'конверсия', 'roi', 'ctr',
            'охват', 'вовлеченность', 'аудитория', 'сегмент', 'креатив',
            'посев', 'размещение', 'интеграция', 'нативная', 'баннер'
        ]
        
        self.telegram_ad_keywords = [
            'telegram', 'телеграм', 'канал', 'чат', 'бот', 'подписчик',
            'просмотр', 'репост', 'пост', 'сторис', 'tgstat', 'телестат',
            'закуп', 'площадка', 'размещение', 'медиакит', 'прайс'
        ]
        
        self.business_keywords = [
            'бизнес', 'стартап', 'предприниматель', 'доход', 'прибыль',
            'инвестиции', 'капитал', 'монетизация', 'заработок', 'деньги',
            'клиент', 'продукт', 'услуга', 'ниша', 'рынок', 'конкуренция'
        ]

    async def analyze_channel_comprehensive(self, channel_id: str, group_id: str = None):
        """Комплексный анализ канала и связанной группы"""
        
        print(f"🔮 Запуск анализа канала Абрамовой {channel_id}...")
        if group_id:
            print(f"📱 Также будет проанализирована связанная группа {group_id}")
        
        try:
            await self.client.start(phone=PHONE)
            print("✅ Подключение к Telegram успешно")
            
            # Анализ основного канала
            channel_result = await self._analyze_entity(channel_id, "channel")
            
            # Анализ связанной группы (если указана)
            group_result = None
            if group_id:
                group_result = await self._analyze_entity(group_id, "group")
            
            # Комплексный анализ
            comprehensive_analysis = await self._comprehensive_analysis(
                channel_result, group_result
            )
            
            # Сохранение результатов
            await self._save_results(channel_result, group_result, comprehensive_analysis)
            
            return {
                'channel': channel_result,
                'group': group_result,
                'comprehensive': comprehensive_analysis
            }
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await self.client.disconnect()

    async def _analyze_entity(self, entity_id: str, entity_type: str):
        """Анализ отдельной сущности (канала или группы)"""
        
        print(f"\n📊 Анализ {entity_type} {entity_id}...")
        
        try:
            # Получаем сущность
            try:
                entity = await self.client.get_entity(int(entity_id))
            except ValueError:
                entity = await self.client.get_entity(entity_id)
            
            # Базовая информация
            entity_info = {
                'id': entity.id,
                'title': getattr(entity, 'title', 'Unknown'),
                'username': getattr(entity, 'username', None),
                'type': 'channel' if isinstance(entity, Channel) else 'group' if isinstance(entity, Chat) else 'user',
                'participants_count': getattr(entity, 'participants_count', 0),
                'description': getattr(entity, 'about', ''),
                'verified': getattr(entity, 'verified', False),
                'scam': getattr(entity, 'scam', False),
                'restricted': getattr(entity, 'restricted', False),
                'megagroup': getattr(entity, 'megagroup', False) if hasattr(entity, 'megagroup') else False
            }
            
            print(f"   📺 {entity_info['title']}")
            print(f"   👥 Подписчиков: {entity_info['participants_count']:,}")
            
            # Сбор сообщений для анализа
            messages = await self._collect_messages(entity, limit=300)  # Больше сообщений для детального анализа
            
            # Анализ контента
            content_analysis = await self._analyze_content(messages, entity_type)
            
            # Анализ активности
            activity_analysis = await self._analyze_activity(messages)
            
            # Анализ аудитории (для групп)
            audience_analysis = None
            if entity_type == "group":
                audience_analysis = await self._analyze_audience(entity)
            
            # Специализированный анализ для маркетингового контента
            marketing_analysis = await self._analyze_marketing_content(messages)
            
            return {
                'entity_info': entity_info,
                'content_analysis': content_analysis,
                'activity_analysis': activity_analysis,
                'audience_analysis': audience_analysis,
                'marketing_analysis': marketing_analysis,
                'messages_sample': messages[:20]  # Сохраняем образцы сообщений
            }
            
        except ChannelPrivateError:
            print(f"❌ {entity_type.capitalize()} приватный или недоступен")
            return None
        except ChatAdminRequiredError:
            print(f"❌ Требуются права администратора для анализа {entity_type}")
            return None
        except Exception as e:
            print(f"❌ Ошибка анализа {entity_type}: {e}")
            return None

    async def _collect_messages(self, entity, limit=300):
        """Сбор сообщений для анализа"""
        
        messages = []
        print(f"   📥 Сбор сообщений (лимит: {limit})...")
        
        try:
            async for message in self.client.iter_messages(entity, limit=limit):
                if message.text or message.media:
                    msg_data = {
                        'id': message.id,
                        'text': message.text or '',
                        'date': message.date.isoformat() if message.date else None,
                        'views': getattr(message, 'views', 0) or 0,
                        'forwards': getattr(message, 'forwards', 0) or 0,
                        'replies': getattr(message.replies, 'replies', 0) if message.replies else 0,
                        'reactions': self._extract_reactions(message),
                        'media_type': self._get_media_type(message),
                        'has_links': bool(re.search(r'http[s]?://|t\.me/', message.text or '')),
                        'has_mentions': bool(re.search(r'@\w+', message.text or '')),
                        'has_hashtags': bool(re.search(r'#\w+', message.text or '')),
                        'word_count': len((message.text or '').split()),
                        'char_count': len(message.text or '')
                    }
                    messages.append(msg_data)
            
            print(f"   ✅ Собрано {len(messages)} сообщений")
            return messages
            
        except Exception as e:
            print(f"   ❌ Ошибка сбора сообщений: {e}")
            return []

    def _extract_reactions(self, message):
        """Извлечение реакций из сообщения"""
        reactions = {}
        if hasattr(message, 'reactions') and message.reactions:
            for reaction in message.reactions.results:
                emoji = reaction.reaction.emoticon if hasattr(reaction.reaction, 'emoticon') else str(reaction.reaction)
                reactions[emoji] = reaction.count
        return reactions

    def _get_media_type(self, message):
        """Определение типа медиа в сообщении"""
        if not message.media:
            return 'text'
        
        media_type = type(message.media).__name__
        if 'Photo' in media_type:
            return 'photo'
        elif 'Video' in media_type or 'Document' in media_type:
            return 'video'
        elif 'Audio' in media_type:
            return 'audio'
        elif 'Sticker' in media_type:
            return 'sticker'
        else:
            return 'other'

    async def _analyze_content(self, messages, entity_type):
        """Анализ контента"""
        
        if not messages:
            return {}
        
        print(f"   🧠 Анализ контента...")
        
        # Базовая статистика
        total_messages = len(messages)
        all_text = ' '.join([msg['text'] for msg in messages if msg['text']])
        words = all_text.split()
        
        # Статистика по медиа
        media_stats = Counter([msg['media_type'] for msg in messages])
        
        # Статистика по активности
        total_views = sum(msg['views'] for msg in messages)
        total_forwards = sum(msg['forwards'] for msg in messages)
        total_replies = sum(msg['replies'] for msg in messages)
        
        # Анализ ключевых слов
        word_freq = Counter()
        for word in words:
            if len(word) > 3:
                clean_word = re.sub(r'[^\w]', '', word.lower())
                if clean_word:
                    word_freq[clean_word] += 1
        
        # Тематический анализ
        marketing_mentions = sum(all_text.lower().count(keyword) for keyword in self.marketing_keywords)
        telegram_ad_mentions = sum(all_text.lower().count(keyword) for keyword in self.telegram_ad_keywords)
        business_mentions = sum(all_text.lower().count(keyword) for keyword in self.business_keywords)
        
        # Анализ времени публикаций
        dates = [datetime.fromisoformat(msg['date'].replace('Z', '+00:00')) 
                for msg in messages if msg['date']]
        
        time_analysis = {}
        if dates:
            # Распределение по часам
            hours = [d.hour for d in dates]
            hour_distribution = Counter(hours)
            
            # Распределение по дням недели
            weekdays = [d.weekday() for d in dates]  # 0 = Monday
            weekday_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
            weekday_distribution = {weekday_names[i]: weekdays.count(i) for i in range(7)}
            
            time_analysis = {
                'most_active_hours': dict(hour_distribution.most_common(5)),
                'weekday_distribution': weekday_distribution,
                'posting_frequency': len(dates) / max((max(dates) - min(dates)).days, 1)
            }
        
        return {
            'statistics': {
                'total_messages': total_messages,
                'total_characters': len(all_text),
                'total_words': len(words),
                'avg_message_length': len(all_text) / total_messages if total_messages > 0 else 0,
                'avg_word_count': sum(msg['word_count'] for msg in messages) / total_messages if total_messages > 0 else 0,
                'total_views': total_views,
                'total_forwards': total_forwards,
                'total_replies': total_replies,
                'avg_views': total_views / total_messages if total_messages > 0 else 0,
                'engagement_rate': (total_forwards + total_replies) / total_views * 100 if total_views > 0 else 0
            },
            'media_distribution': dict(media_stats),
            'top_words': dict(word_freq.most_common(20)),
            'thematic_analysis': {
                'marketing_focus': marketing_mentions,
                'telegram_advertising_focus': telegram_ad_mentions,
                'business_focus': business_mentions,
                'main_theme_score': max(marketing_mentions, telegram_ad_mentions, business_mentions)
            },
            'time_analysis': time_analysis,
            'content_features': {
                'messages_with_links': sum(1 for msg in messages if msg['has_links']),
                'messages_with_mentions': sum(1 for msg in messages if msg['has_mentions']),
                'messages_with_hashtags': sum(1 for msg in messages if msg['has_hashtags']),
                'link_percentage': sum(1 for msg in messages if msg['has_links']) / total_messages * 100 if total_messages > 0 else 0
            }
        }

    async def _analyze_activity(self, messages):
        """Анализ активности"""
        
        if not messages:
            return {}
        
        print(f"   📈 Анализ активности...")
        
        # Сортируем сообщения по дате
        dated_messages = [msg for msg in messages if msg['date']]
        dated_messages.sort(key=lambda x: x['date'])
        
        if not dated_messages:
            return {}
        
        # Анализ трендов
        recent_messages = dated_messages[-30:]  # Последние 30 сообщений
        older_messages = dated_messages[:-30] if len(dated_messages) > 30 else []
        
        recent_avg_views = sum(msg['views'] for msg in recent_messages) / len(recent_messages) if recent_messages else 0
        older_avg_views = sum(msg['views'] for msg in older_messages) / len(older_messages) if older_messages else 0
        
        # Топ сообщения по просмотрам
        top_messages = sorted(messages, key=lambda x: x['views'], reverse=True)[:10]
        
        # Анализ регулярности
        if len(dated_messages) > 1:
            dates = [datetime.fromisoformat(msg['date'].replace('Z', '+00:00')) for msg in dated_messages]
            intervals = [(dates[i] - dates[i-1]).total_seconds() / 3600 for i in range(1, len(dates))]  # в часах
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
        else:
            avg_interval = 0
        
        return {
            'trend_analysis': {
                'recent_avg_views': recent_avg_views,
                'older_avg_views': older_avg_views,
                'growth_trend': 'растущий' if recent_avg_views > older_avg_views else 'снижающийся' if recent_avg_views < older_avg_views else 'стабильный'
            },
            'top_performing_messages': [
                {
                    'id': msg['id'],
                    'views': msg['views'],
                    'text_preview': msg['text'][:100] + '...' if len(msg['text']) > 100 else msg['text'],
                    'engagement': msg['forwards'] + msg['replies']
                }
                for msg in top_messages
            ],
            'posting_regularity': {
                'avg_interval_hours': avg_interval,
                'posting_consistency': 'высокая' if avg_interval < 48 else 'средняя' if avg_interval < 168 else 'низкая'
            }
        }

    async def _analyze_audience(self, entity):
        """Анализ аудитории (для групп)"""
        
        print(f"   👥 Анализ аудитории...")
        
        try:
            # Получаем участников (ограниченное количество)
            participants = []
            async for user in self.client.iter_participants(entity, limit=100):
                if isinstance(user, User):
                    participants.append({
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_bot': user.bot,
                        'is_premium': getattr(user, 'premium', False),
                        'phone': user.phone if hasattr(user, 'phone') else None
                    })
            
            # Анализ участников
            total_participants = len(participants)
            bot_count = sum(1 for p in participants if p['is_bot'])
            premium_count = sum(1 for p in participants if p['is_premium'])
            with_username = sum(1 for p in participants if p['username'])
            
            return {
                'sample_size': total_participants,
                'bot_percentage': bot_count / total_participants * 100 if total_participants > 0 else 0,
                'premium_percentage': premium_count / total_participants * 100 if total_participants > 0 else 0,
                'username_percentage': with_username / total_participants * 100 if total_participants > 0 else 0,
                'quality_score': (100 - (bot_count / total_participants * 100)) if total_participants > 0 else 0
            }
            
        except Exception as e:
            print(f"   ❌ Ошибка анализа аудитории: {e}")
            return {'error': str(e)}

    async def _analyze_marketing_content(self, messages):
        """Специализированный анализ маркетингового контента"""
        
        print(f"   🎯 Анализ маркетингового контента...")
        
        if not messages:
            return {}
        
        # Поиск рекламных постов
        ad_posts = []
        educational_posts = []
        personal_posts = []
        
        for msg in messages:
            text = msg['text'].lower()
            
            # Признаки рекламного поста
            ad_indicators = ['реклама', 'размещение', 'заказать', 'прайс', 'стоимость', 'услуги', 'предложение']
            if any(indicator in text for indicator in ad_indicators):
                ad_posts.append(msg)
            
            # Признаки образовательного контента
            edu_indicators = ['как', 'способ', 'метод', 'инструкция', 'гайд', 'совет', 'секрет', 'правило']
            if any(indicator in text for indicator in edu_indicators):
                educational_posts.append(msg)
            
            # Признаки личного контента
            personal_indicators = ['я', 'мой', 'моя', 'мне', 'история', 'опыт', 'считаю', 'думаю']
            if any(indicator in text for indicator in personal_indicators):
                personal_posts.append(msg)
        
        # Анализ CTA (призывов к действию)
        cta_patterns = [
            r'подписывайтесь',
            r'переходите',
            r'жмите',
            r'кликайте',
            r'заказывайте',
            r'пишите',
            r'звоните',
            r'регистрируйтесь'
        ]
        
        messages_with_cta = []
        for msg in messages:
            if any(re.search(pattern, msg['text'].lower()) for pattern in cta_patterns):
                messages_with_cta.append(msg)
        
        # Анализ лид-магнитов
        leadmagnet_indicators = ['бесплатно', 'скачать', 'получить', 'чек-лист', 'гайд', 'шаблон', 'курс']
        leadmagnet_posts = []
        for msg in messages:
            if any(indicator in msg['text'].lower() for indicator in leadmagnet_indicators):
                leadmagnet_posts.append(msg)
        
        return {
            'content_distribution': {
                'advertising_posts': len(ad_posts),
                'educational_posts': len(educational_posts),
                'personal_posts': len(personal_posts),
                'other_posts': len(messages) - len(ad_posts) - len(educational_posts) - len(personal_posts)
            },
            'cta_analysis': {
                'messages_with_cta': len(messages_with_cta),
                'cta_percentage': len(messages_with_cta) / len(messages) * 100 if messages else 0
            },
            'leadmagnet_analysis': {
                'leadmagnet_posts': len(leadmagnet_posts),
                'leadmagnet_percentage': len(leadmagnet_posts) / len(messages) * 100 if messages else 0
            },
            'top_ad_posts': sorted(ad_posts, key=lambda x: x['views'], reverse=True)[:5],
            'top_educational_posts': sorted(educational_posts, key=lambda x: x['views'], reverse=True)[:5]
        }

    async def _comprehensive_analysis(self, channel_result, group_result):
        """Комплексный анализ канала и группы"""
        
        print(f"\n🎯 Комплексный анализ...")
        
        analysis = {
            'overall_assessment': {},
            'recommendations': [],
            'monetization_potential': {},
            'growth_strategy': {},
            'competitive_analysis': {}
        }
        
        if channel_result:
            channel_stats = channel_result['content_analysis']['statistics']
            marketing_analysis = channel_result['marketing_analysis']
            
            # Общая оценка канала
            analysis['overall_assessment'] = {
                'channel_size': 'большой' if channel_result['entity_info']['participants_count'] > 10000 else 'средний' if channel_result['entity_info']['participants_count'] > 1000 else 'малый',
                'engagement_level': 'высокий' if channel_stats['engagement_rate'] > 5 else 'средний' if channel_stats['engagement_rate'] > 1 else 'низкий',
                'content_quality': 'высокое' if channel_stats['avg_message_length'] > 500 else 'среднее' if channel_stats['avg_message_length'] > 200 else 'низкое',
                'posting_frequency': channel_result['content_analysis']['time_analysis'].get('posting_frequency', 0),
                'marketing_focus_score': marketing_analysis['content_distribution']['advertising_posts'] + marketing_analysis['content_distribution']['educational_posts']
            }
            
            # Рекомендации
            recommendations = []
            
            if channel_stats['engagement_rate'] < 2:
                recommendations.append("Увеличить вовлеченность аудитории через интерактивный контент")
            
            if marketing_analysis['cta_analysis']['cta_percentage'] < 30:
                recommendations.append("Добавить больше призывов к действию в посты")
            
            if marketing_analysis['leadmagnet_analysis']['leadmagnet_percentage'] < 10:
                recommendations.append("Создать больше лид-магнитов для сбора контактов")
            
            if channel_result['content_analysis']['content_features']['link_percentage'] < 20:
                recommendations.append("Увеличить количество полезных ссылок в контенте")
            
            analysis['recommendations'] = recommendations
            
            # Потенциал монетизации
            analysis['monetization_potential'] = {
                'advertising_revenue': 'высокий' if channel_result['entity_info']['participants_count'] > 5000 else 'средний',
                'product_sales': 'высокий' if marketing_analysis['leadmagnet_analysis']['leadmagnet_percentage'] > 15 else 'средний',
                'consultation_services': 'высокий' if marketing_analysis['content_distribution']['educational_posts'] > 20 else 'средний',
                'course_creation': 'высокий' if channel_result['content_analysis']['thematic_analysis']['marketing_focus'] > 50 else 'средний'
            }
        
        return analysis

    async def _save_results(self, channel_result, group_result, comprehensive_analysis):
        """Сохранение результатов анализа"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создаем папку для результатов
        os.makedirs("analysis/abramova", exist_ok=True)
        
        # Сохраняем полный результат
        full_result = {
            'analysis_date': datetime.now().isoformat(),
            'channel_analysis': channel_result,
            'group_analysis': group_result,
            'comprehensive_analysis': comprehensive_analysis
        }
        
        filename = f"analysis/abramova/abramova_channel_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Полный анализ сохранен в: {filename}")
        
        # Создаем краткий отчет
        await self._create_summary_report(full_result, timestamp)

    async def _create_summary_report(self, full_result, timestamp):
        """Создание краткого отчета"""
        
        report_filename = f"analysis/abramova/abramova_summary_report_{timestamp}.md"
        
        channel = full_result['channel_analysis']
        comprehensive = full_result['comprehensive_analysis']
        
        report_content = f"""# Анализ канала Абрамовой - Краткий отчет

**Дата анализа:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

## 📊 Основные показатели

### Канал
- **Название:** {channel['entity_info']['title']}
- **Подписчиков:** {channel['entity_info']['participants_count']:,}
- **Тип:** {channel['entity_info']['type']}
- **Username:** @{channel['entity_info']['username'] or 'не указан'}

### Статистика контента
- **Проанализировано сообщений:** {channel['content_analysis']['statistics']['total_messages']}
- **Средние просмотры:** {channel['content_analysis']['statistics']['avg_views']:.0f}
- **Коэффициент вовлеченности:** {channel['content_analysis']['statistics']['engagement_rate']:.2f}%
- **Средняя длина сообщения:** {channel['content_analysis']['statistics']['avg_message_length']:.0f} символов

## 🎯 Тематический анализ

### Фокус контента
- **Маркетинг:** {channel['content_analysis']['thematic_analysis']['marketing_focus']} упоминаний
- **Реклама в Telegram:** {channel['content_analysis']['thematic_analysis']['telegram_advertising_focus']} упоминаний  
- **Бизнес:** {channel['content_analysis']['thematic_analysis']['business_focus']} упоминаний

### Распределение контента
- **Рекламные посты:** {channel['marketing_analysis']['content_distribution']['advertising_posts']}
- **Образовательные посты:** {channel['marketing_analysis']['content_distribution']['educational_posts']}
- **Личные посты:** {channel['marketing_analysis']['content_distribution']['personal_posts']}

## 📈 Маркетинговый анализ

### Призывы к действию
- **Постов с CTA:** {channel['marketing_analysis']['cta_analysis']['messages_with_cta']} ({channel['marketing_analysis']['cta_analysis']['cta_percentage']:.1f}%)

### Лид-магниты
- **Постов с лид-магнитами:** {channel['marketing_analysis']['leadmagnet_analysis']['leadmagnet_posts']} ({channel['marketing_analysis']['leadmagnet_analysis']['leadmagnet_percentage']:.1f}%)

## 🎯 Общая оценка

- **Размер канала:** {comprehensive['overall_assessment']['channel_size']}
- **Уровень вовлеченности:** {comprehensive['overall_assessment']['engagement_level']}
- **Качество контента:** {comprehensive['overall_assessment']['content_quality']}
- **Частота публикаций:** {comprehensive['overall_assessment']['posting_frequency']:.1f} постов/день

## 💡 Рекомендации

"""
        
        for i, rec in enumerate(comprehensive['recommendations'], 1):
            report_content += f"{i}. {rec}\n"
        
        report_content += f"""
## 💰 Потенциал монетизации

- **Доходы от рекламы:** {comprehensive['monetization_potential']['advertising_revenue']}
- **Продажа продуктов:** {comprehensive['monetization_potential']['product_sales']}
- **Консультационные услуги:** {comprehensive['monetization_potential']['consultation_services']}
- **Создание курсов:** {comprehensive['monetization_potential']['course_creation']}

## 🔝 Топ сообщения по просмотрам

"""
        
        for i, msg in enumerate(channel['activity_analysis']['top_performing_messages'][:5], 1):
            report_content += f"{i}. **{msg['views']:,} просмотров** - {msg['text_preview']}\n"
        
        report_content += f"""
## 📊 Топ слова в контенте

"""
        
        top_words = list(channel['content_analysis']['top_words'].items())[:10]
        for word, count in top_words:
            report_content += f"- **{word}:** {count} упоминаний\n"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Краткий отчет сохранен в: {report_filename}")

async def main():
    """Главная функция"""
    print("🔮 АНАЛИЗ КАНАЛА АБРАМОВОЙ")
    print("="*60)
    print("📺 Канал: 1681841249")
    print("👥 Связанная группа: 1605750182")
    print("="*60)
    
    analyzer = AbramovaChannelAnalyzer()
    
    result = await analyzer.analyze_channel_comprehensive(
        channel_id='1681841249',
        group_id='1605750182'
    )
    
    if result:
        print("\n✅ Анализ завершен успешно!")
        if result['channel']:
            channel_info = result['channel']['entity_info']
            stats = result['channel']['content_analysis']['statistics']
            print(f"📊 Канал: {channel_info['title']}")
            print(f"👥 Подписчиков: {channel_info['participants_count']:,}")
            print(f"📈 Проанализировано сообщений: {stats['total_messages']}")
            print(f"💬 Средняя вовлеченность: {stats['engagement_rate']:.2f}%")
        
        if result['group']:
            group_info = result['group']['entity_info']
            print(f"👥 Группа: {group_info['title']}")
            print(f"👤 Участников: {group_info['participants_count']:,}")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
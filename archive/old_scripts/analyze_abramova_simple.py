#!/usr/bin/env python3
"""
Простой анализатор каналов Абрамовой с обработкой ошибок доступа
"""

import asyncio
import os
import json
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError, FloodWaitError
import re
from collections import Counter

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

async def analyze_abramova_channels():
    """Анализ каналов Абрамовой с обработкой ошибок"""
    
    # Каналы для анализа
    channels_to_analyze = [
        {'id': '1681841249', 'name': 'Основной канал Абрамовой', 'type': 'channel'},
        {'id': '1605750182', 'name': 'Связанная группа', 'type': 'group'},
        {'id': '1264917018', 'name': 'Диалог с заказчицей', 'type': 'dialog'}
    ]
    
    print("🔮 АНАЛИЗ КАНАЛОВ АБРАМОВОЙ")
    print("="*60)
    
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    results = {}
    
    try:
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        for channel_info in channels_to_analyze:
            channel_id = channel_info['id']
            channel_name = channel_info['name']
            channel_type = channel_info['type']
            
            print(f"\n📊 Анализ {channel_name} ({channel_id})...")
            
            try:
                # Пробуем получить сущность
                try:
                    entity = await client.get_entity(int(channel_id))
                except ValueError:
                    entity = await client.get_entity(channel_id)
                except Exception as e:
                    print(f"   ❌ Не удалось получить сущность: {e}")
                    continue
                
                # Базовая информация
                entity_info = {
                    'id': entity.id,
                    'title': getattr(entity, 'title', 'Unknown'),
                    'username': getattr(entity, 'username', None),
                    'type': 'channel' if isinstance(entity, Channel) else 'group' if isinstance(entity, Chat) else 'user',
                    'participants_count': getattr(entity, 'participants_count', 0) or 0,
                    'description': getattr(entity, 'about', ''),
                    'verified': getattr(entity, 'verified', False),
                    'scam': getattr(entity, 'scam', False)
                }
                
                print(f"   📺 {entity_info['title']}")
                print(f"   👥 Подписчиков: {entity_info['participants_count']:,}")
                print(f"   🔗 Username: @{entity_info['username'] or 'не указан'}")
                
                # Сбор сообщений
                messages = []
                message_count = 0
                total_views = 0
                total_forwards = 0
                total_replies = 0
                
                print(f"   📥 Сбор сообщений...")
                
                try:
                    async for message in client.iter_messages(entity, limit=200):
                        if message.text:
                            message_count += 1
                            views = getattr(message, 'views', 0) or 0
                            forwards = getattr(message, 'forwards', 0) or 0
                            replies = getattr(message.replies, 'replies', 0) if message.replies else 0
                            
                            total_views += views
                            total_forwards += forwards
                            total_replies += replies
                            
                            messages.append({
                                'id': message.id,
                                'text': message.text,
                                'date': message.date.isoformat() if message.date else None,
                                'views': views,
                                'forwards': forwards,
                                'replies': replies,
                                'has_links': bool(re.search(r'http[s]?://|t\.me/', message.text or '')),
                                'has_mentions': bool(re.search(r'@\w+', message.text or '')),
                                'word_count': len(message.text.split()) if message.text else 0
                            })
                    
                    print(f"   ✅ Собрано {len(messages)} сообщений")
                    
                except Exception as e:
                    print(f"   ⚠️ Ошибка сбора сообщений: {e}")
                    messages = []
                
                # Анализ контента
                content_analysis = analyze_content(messages)
                
                # Маркетинговый анализ
                marketing_analysis = analyze_marketing_content(messages)
                
                # Сохраняем результат
                results[channel_id] = {
                    'entity_info': entity_info,
                    'content_analysis': content_analysis,
                    'marketing_analysis': marketing_analysis,
                    'messages_sample': messages[:10]  # Первые 10 сообщений
                }
                
                print(f"   ✅ Анализ завершен")
                
            except ChannelPrivateError:
                print(f"   ❌ Канал приватный или недоступен")
                results[channel_id] = {'error': 'private_channel'}
            except ChatAdminRequiredError:
                print(f"   ❌ Требуются права администратора")
                results[channel_id] = {'error': 'admin_required'}
            except FloodWaitError as e:
                print(f"   ❌ Превышен лимит запросов, ожидание {e.seconds} секунд")
                results[channel_id] = {'error': f'flood_wait_{e.seconds}'}
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                results[channel_id] = {'error': str(e)}
        
        # Сохранение результатов
        await save_results(results)
        
        return results
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await client.disconnect()

def analyze_content(messages):
    """Анализ контента сообщений"""
    
    if not messages:
        return {'error': 'no_messages'}
    
    # Базовая статистика
    total_messages = len(messages)
    all_text = ' '.join([msg['text'] for msg in messages if msg['text']])
    words = all_text.split()
    
    total_views = sum(msg['views'] for msg in messages)
    total_forwards = sum(msg['forwards'] for msg in messages)
    total_replies = sum(msg['replies'] for msg in messages)
    
    # Анализ ключевых слов
    marketing_keywords = [
        'реклама', 'маркетинг', 'продвижение', 'таргет', 'smm', 'контент',
        'бренд', 'продажи', 'воронка', 'лид', 'конверсия', 'roi', 'ctr',
        'охват', 'вовлеченность', 'аудитория', 'сегмент', 'креатив'
    ]
    
    telegram_keywords = [
        'telegram', 'телеграм', 'канал', 'чат', 'бот', 'подписчик',
        'просмотр', 'репост', 'пост', 'tgstat', 'закуп', 'размещение'
    ]
    
    business_keywords = [
        'бизнес', 'стартап', 'предприниматель', 'доход', 'прибыль',
        'инвестиции', 'монетизация', 'заработок', 'клиент', 'продукт'
    ]
    
    text_lower = all_text.lower()
    
    # Подсчет упоминаний
    marketing_mentions = sum(text_lower.count(keyword) for keyword in marketing_keywords)
    telegram_mentions = sum(text_lower.count(keyword) for keyword in telegram_keywords)
    business_mentions = sum(text_lower.count(keyword) for keyword in business_keywords)
    
    # Частотность слов
    word_freq = Counter()
    for word in words:
        if len(word) > 3:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word:
                word_freq[clean_word] += 1
    
    return {
        'statistics': {
            'total_messages': total_messages,
            'total_characters': len(all_text),
            'total_words': len(words),
            'avg_message_length': len(all_text) / total_messages if total_messages > 0 else 0,
            'total_views': total_views,
            'total_forwards': total_forwards,
            'total_replies': total_replies,
            'avg_views': total_views / total_messages if total_messages > 0 else 0,
            'engagement_rate': (total_forwards + total_replies) / total_views * 100 if total_views > 0 else 0
        },
        'thematic_analysis': {
            'marketing_focus': marketing_mentions,
            'telegram_focus': telegram_mentions,
            'business_focus': business_mentions
        },
        'top_words': dict(word_freq.most_common(20)),
        'content_features': {
            'messages_with_links': sum(1 for msg in messages if msg['has_links']),
            'messages_with_mentions': sum(1 for msg in messages if msg['has_mentions']),
            'avg_word_count': sum(msg['word_count'] for msg in messages) / total_messages if total_messages > 0 else 0
        }
    }

def analyze_marketing_content(messages):
    """Анализ маркетингового контента"""
    
    if not messages:
        return {'error': 'no_messages'}
    
    # Поиск рекламных постов
    ad_indicators = ['реклама', 'размещение', 'заказать', 'прайс', 'стоимость', 'услуги']
    edu_indicators = ['как', 'способ', 'метод', 'инструкция', 'гайд', 'совет', 'секрет']
    personal_indicators = ['я', 'мой', 'моя', 'мне', 'история', 'опыт', 'считаю']
    
    ad_posts = 0
    educational_posts = 0
    personal_posts = 0
    
    for msg in messages:
        text = msg['text'].lower() if msg['text'] else ''
        
        if any(indicator in text for indicator in ad_indicators):
            ad_posts += 1
        elif any(indicator in text for indicator in edu_indicators):
            educational_posts += 1
        elif any(indicator in text for indicator in personal_indicators):
            personal_posts += 1
    
    # Анализ CTA
    cta_patterns = [
        r'подписывайтесь', r'переходите', r'жмите', r'кликайте',
        r'заказывайте', r'пишите', r'звоните', r'регистрируйтесь'
    ]
    
    messages_with_cta = 0
    for msg in messages:
        if msg['text'] and any(re.search(pattern, msg['text'].lower()) for pattern in cta_patterns):
            messages_with_cta += 1
    
    # Анализ лид-магнитов
    leadmagnet_indicators = ['бесплатно', 'скачать', 'получить', 'чек-лист', 'гайд', 'шаблон']
    leadmagnet_posts = 0
    for msg in messages:
        if msg['text'] and any(indicator in msg['text'].lower() for indicator in leadmagnet_indicators):
            leadmagnet_posts += 1
    
    total_messages = len(messages)
    
    return {
        'content_distribution': {
            'advertising_posts': ad_posts,
            'educational_posts': educational_posts,
            'personal_posts': personal_posts,
            'other_posts': total_messages - ad_posts - educational_posts - personal_posts
        },
        'cta_analysis': {
            'messages_with_cta': messages_with_cta,
            'cta_percentage': messages_with_cta / total_messages * 100 if total_messages > 0 else 0
        },
        'leadmagnet_analysis': {
            'leadmagnet_posts': leadmagnet_posts,
            'leadmagnet_percentage': leadmagnet_posts / total_messages * 100 if total_messages > 0 else 0
        }
    }

async def save_results(results):
    """Сохранение результатов анализа"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Создаем папку для результатов
    os.makedirs("analysis/abramova", exist_ok=True)
    
    # Сохраняем полный результат
    full_result = {
        'analysis_date': datetime.now().isoformat(),
        'results': results
    }
    
    filename = f"analysis/abramova/abramova_channels_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(full_result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 Результаты сохранены в: {filename}")
    
    # Создаем краткий отчет
    await create_summary_report(results, timestamp)

async def create_summary_report(results, timestamp):
    """Создание краткого отчета"""
    
    report_filename = f"analysis/abramova/abramova_channels_report_{timestamp}.md"
    
    report_content = f"""# Анализ каналов Абрамовой - Отчет

**Дата анализа:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

## 📊 Результаты анализа

"""
    
    for channel_id, data in results.items():
        if 'error' in data:
            report_content += f"""### Канал {channel_id}
❌ **Ошибка:** {data['error']}

"""
        else:
            entity_info = data['entity_info']
            content_analysis = data['content_analysis']
            marketing_analysis = data['marketing_analysis']
            
            report_content += f"""### {entity_info['title']}
- **ID:** {channel_id}
- **Тип:** {entity_info['type']}
- **Подписчиков:** {entity_info['participants_count']:,}
- **Username:** @{entity_info['username'] or 'не указан'}

#### Статистика контента
- **Сообщений проанализировано:** {content_analysis['statistics']['total_messages']}
- **Средние просмотры:** {content_analysis['statistics']['avg_views']:.0f}
- **Вовлеченность:** {content_analysis['statistics']['engagement_rate']:.2f}%
- **Средняя длина сообщения:** {content_analysis['statistics']['avg_message_length']:.0f} символов

#### Тематический анализ
- **Маркетинг:** {content_analysis['thematic_analysis']['marketing_focus']} упоминаний
- **Telegram:** {content_analysis['thematic_analysis']['telegram_focus']} упоминаний
- **Бизнес:** {content_analysis['thematic_analysis']['business_focus']} упоминаний

#### Маркетинговый контент
- **Рекламные посты:** {marketing_analysis['content_distribution']['advertising_posts']}
- **Образовательные посты:** {marketing_analysis['content_distribution']['educational_posts']}
- **Личные посты:** {marketing_analysis['content_distribution']['personal_posts']}
- **CTA в постах:** {marketing_analysis['cta_analysis']['cta_percentage']:.1f}%
- **Лид-магниты:** {marketing_analysis['leadmagnet_analysis']['leadmagnet_percentage']:.1f}%

#### Топ слова
"""
            
            if 'top_words' in content_analysis:
                top_words = list(content_analysis['top_words'].items())[:10]
                for word, count in top_words:
                    report_content += f"- **{word}:** {count}\n"
            
            report_content += "\n---\n\n"
    
    # Общие рекомендации
    report_content += """## 💡 Общие рекомендации

### На основе анализа доступных данных:

1. **Увеличение вовлеченности:**
   - Добавить больше интерактивного контента
   - Использовать опросы и вопросы к аудитории
   - Создавать контент, стимулирующий обсуждения

2. **Оптимизация контент-стратегии:**
   - Соблюдать баланс: 70% образовательный, 20% личный, 10% продающий контент
   - Увеличить количество призывов к действию
   - Создать больше лид-магнитов

3. **Развитие монетизации:**
   - Разработать систему лид-магнитов
   - Создать воронки продаж
   - Оптимизировать рекламные размещения

4. **Техническая оптимизация:**
   - Регулярно анализировать статистику
   - A/B тестировать разные форматы контента
   - Отслеживать конверсии и ROI

## 📈 Следующие шаги

1. Получить доступ к закрытым каналам для полного анализа
2. Провести анализ конкурентов
3. Создать детальную контент-стратегию
4. Разработать систему автоматизации
5. Запустить тестовые рекламные кампании

"""
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 Отчет сохранен в: {report_filename}")

async def main():
    """Главная функция"""
    result = await analyze_abramova_channels()
    
    if result:
        print("\n✅ Анализ завершен!")
        
        # Подсчет успешных анализов
        successful = sum(1 for data in result.values() if 'error' not in data)
        total = len(result)
        
        print(f"📊 Успешно проанализировано: {successful}/{total} каналов")
        
        # Показываем краткую статистику по доступным каналам
        for channel_id, data in result.items():
            if 'error' not in data:
                entity_info = data['entity_info']
                stats = data['content_analysis']['statistics']
                print(f"   📺 {entity_info['title']}: {stats['total_messages']} сообщений, {stats['avg_views']:.0f} средних просмотров")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
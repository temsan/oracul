#!/usr/bin/env python3
"""
Анализ диалога с пользователем 803284614 для оценки шансов получить проект
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import User
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError

# Настройки из .env
API_ID = int(os.getenv('TG_API_ID', '21834116'))
API_HASH = os.getenv('TG_API_HASH', '3139c483fb576f2043610eb2ba7e285e')
PHONE = os.getenv('TG_PHONE', '+79968202246')
SESSION_FILE = 'oracul.session'

async def analyze_dialog_for_project():
    """Анализ диалога с пользователем 803284614 для оценки шансов получить проект"""
    
    user_id = 803284614
    print(f"🔮 Анализ диалога с пользователем {user_id} для оценки проекта...")
    
    # Создаем клиент
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        # Подключаемся
        await client.start(phone=PHONE)
        print("✅ Подключение к Telegram успешно")
        
        # Получаем информацию о пользователе
        try:
            user = await client.get_entity(user_id)
        except Exception as e:
            print(f"❌ Не удалось получить информацию о пользователе: {e}")
            return None
        
        # Базовая информация о пользователе
        user_info = {
            'id': user.id,
            'first_name': getattr(user, 'first_name', None),
            'last_name': getattr(user, 'last_name', None),
            'username': getattr(user, 'username', None),
            'is_bot': getattr(user, 'bot', False),
            'is_verified': getattr(user, 'verified', False),
            'is_premium': getattr(user, 'premium', False),
            'status': str(getattr(user, 'status', 'Unknown'))
        }
        
        print(f"\n👤 ИНФОРМАЦИЯ О СОБЕСЕДНИКЕ:")
        print(f"   Имя: {user_info['first_name'] or 'Не указано'} {user_info['last_name'] or ''}")
        print(f"   Username: @{user_info['username'] or 'Не указан'}")
        print(f"   Статус: {user_info['status']}")
        print(f"   Premium: {'Да' if user_info['is_premium'] else 'Нет'}")
        
        # Получаем историю сообщений
        messages = []
        try:
            print(f"\n📊 Получение истории диалога...")
            async for message in client.iter_messages(user, limit=200):
                if message.text or message.media:
                    messages.append({
                        'id': message.id,
                        'text': message.text or '[Медиа]',
                        'date': message.date.isoformat() if message.date else None,
                        'from_id': message.from_id.user_id if message.from_id else None,
                        'is_outgoing': message.out,
                        'reply_to': message.reply_to.reply_to_msg_id if message.reply_to else None,
                        'has_media': bool(message.media)
                    })
            
            print(f"✅ Получено {len(messages)} сообщений")
            
        except Exception as e:
            print(f"❌ Ошибка получения сообщений: {e}")
            return None
        
        if not messages:
            print("❌ Нет сообщений для анализа")
            return None
        
        # Сортируем сообщения по дате (от старых к новым)
        messages.sort(key=lambda x: x['date'] if x['date'] else '')
        
        # Анализ диалога
        analysis = analyze_conversation_for_project(messages, user_info)
        
        # Показываем результаты
        print_analysis_results(analysis, messages)
        
        # Сохраняем результат
        result = {
            'user_info': user_info,
            'messages': messages,
            'analysis': analysis,
            'analysis_date': datetime.now().isoformat()
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Определяем имя для файла
        name = user_info['first_name'] or 'unknown'
        if user_info['last_name']:
            name += f"_{user_info['last_name']}"
        name = name.lower().replace(' ', '_')
        
        os.makedirs("analysis/project_analysis", exist_ok=True)
        filename = f"analysis/project_analysis/dialog_{name}_project_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Результат сохранен в: {filename}")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await client.disconnect()

def analyze_conversation_for_project(messages, user_info):
    """Анализ диалога для оценки шансов получить проект"""
    
    # Базовая статистика
    total_messages = len(messages)
    my_messages = [msg for msg in messages if msg['is_outgoing']]
    their_messages = [msg for msg in messages if not msg['is_outgoing']]
    
    # Временной анализ
    if messages:
        first_date = datetime.fromisoformat(messages[0]['date'].replace('Z', '+00:00'))
        last_date = datetime.fromisoformat(messages[-1]['date'].replace('Z', '+00:00'))
        conversation_duration = (last_date - first_date).days
        
        # Последняя активность
        last_activity = (datetime.now(last_date.tzinfo) - last_date).days
    else:
        conversation_duration = 0
        last_activity = 999
    
    # Анализ содержания
    all_text = ' '.join([msg['text'] for msg in messages if msg['text']])
    text_lower = all_text.lower()
    
    # Ключевые слова для проектов
    project_keywords = [
        'проект', 'работа', 'задача', 'заказ', 'сотрудничество', 'разработка',
        'деньги', 'оплата', 'бюджет', 'стоимость', 'цена', 'тариф',
        'срок', 'дедлайн', 'время', 'когда', 'готов', 'можете',
        'нужно', 'требуется', 'ищу', 'найти', 'помочь', 'сделать'
    ]
    
    positive_keywords = [
        'отлично', 'хорошо', 'подходит', 'согласен', 'да', 'конечно',
        'интересно', 'понравилось', 'впечатлен', 'качественно', 'профессионально'
    ]
    
    negative_keywords = [
        'нет', 'не подходит', 'дорого', 'долго', 'сложно', 'не нужно',
        'отказ', 'передумал', 'не получится', 'проблема'
    ]
    
    urgency_keywords = [
        'срочно', 'быстро', 'скорее', 'асап', 'вчера', 'немедленно',
        'горит', 'критично', 'важно'
    ]
    
    # Подсчет ключевых слов (ищем целые слова)
    import re
    
    def count_whole_words(text, words):
        count = 0
        for word in words:
            # Ищем целые слова с границами \b
            pattern = r'\b' + re.escape(word) + r'\b'
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    project_mentions = count_whole_words(text_lower, project_keywords)
    positive_signals = count_whole_words(text_lower, positive_keywords)
    negative_signals = count_whole_words(text_lower, negative_keywords)
    urgency_signals = count_whole_words(text_lower, urgency_keywords)
    
    # Анализ паттернов общения
    response_ratio = len(their_messages) / len(my_messages) if my_messages else 0
    avg_my_length = sum(len(msg['text'] or '') for msg in my_messages) / len(my_messages) if my_messages else 0
    avg_their_length = sum(len(msg['text'] or '') for msg in their_messages) / len(their_messages) if their_messages else 0
    
    # Анализ инициативы
    who_started = 'me' if messages and messages[0]['is_outgoing'] else 'them'
    who_last = 'me' if messages and messages[-1]['is_outgoing'] else 'them'
    
    # Оценка шансов (0-100%)
    chance_score = calculate_project_chance(
        project_mentions, positive_signals, negative_signals, urgency_signals,
        response_ratio, conversation_duration, last_activity, who_last,
        len(my_messages), len(their_messages)
    )
    
    return {
        'total_messages': total_messages,
        'my_messages_count': len(my_messages),
        'their_messages_count': len(their_messages),
        'conversation_duration_days': conversation_duration,
        'last_activity_days': last_activity,
        'response_ratio': response_ratio,
        'avg_my_message_length': avg_my_length,
        'avg_their_message_length': avg_their_length,
        'who_started': who_started,
        'who_last_messaged': who_last,
        'project_mentions': project_mentions,
        'positive_signals': positive_signals,
        'negative_signals': negative_signals,
        'urgency_signals': urgency_signals,
        'project_chance_percent': chance_score,
        'recommendation': get_recommendation(chance_score, last_activity, who_last)
    }

def calculate_project_chance(project_mentions, positive_signals, negative_signals, 
                           urgency_signals, response_ratio, duration, last_activity, 
                           who_last, my_count, their_count):
    """Расчет шансов получить проект (0-100%)"""
    
    score = 50  # Базовый уровень
    
    # Позитивные факторы
    score += min(project_mentions * 5, 20)  # Упоминания проекта (+5 за каждое, макс 20)
    score += min(positive_signals * 3, 15)  # Позитивные сигналы (+3 за каждый, макс 15)
    score += min(urgency_signals * 4, 12)   # Срочность (+4 за каждый, макс 12)
    
    # Коэффициент ответов
    if response_ratio > 0.8:
        score += 15  # Активно отвечают
    elif response_ratio > 0.5:
        score += 8   # Средняя активность
    elif response_ratio < 0.3:
        score -= 10  # Слабая активность
    
    # Длительность диалога
    if duration > 7:
        score += 10  # Долгий диалог - хороший знак
    elif duration > 3:
        score += 5
    elif duration == 0:
        score -= 5   # Только сегодня начали
    
    # Последняя активность
    if last_activity == 0:
        score += 10  # Сегодня общались
    elif last_activity <= 1:
        score += 5   # Вчера
    elif last_activity <= 3:
        score += 0   # 2-3 дня назад
    elif last_activity <= 7:
        score -= 5   # Неделя назад
    else:
        score -= 15  # Давно не общались
    
    # Кто последний писал
    if who_last == 'them':
        score += 8   # Они последние писали - хороший знак
    else:
        score -= 3   # Мы последние писали - ждем ответа
    
    # Негативные факторы
    score -= min(negative_signals * 5, 25)  # Негативные сигналы (-5 за каждый)
    
    # Баланс сообщений
    if their_count == 0:
        score -= 30  # Не отвечают вообще
    elif my_count > their_count * 3:
        score -= 15  # Мы пишем слишком много
    
    return max(0, min(100, score))

def get_recommendation(chance_score, last_activity, who_last):
    """Получить рекомендацию по действиям"""
    
    if chance_score >= 80:
        return "ВЫСОКИЕ ШАНСЫ: Активно продолжайте диалог, обсуждайте детали проекта"
    elif chance_score >= 60:
        return "ХОРОШИЕ ШАНСЫ: Предложите конкретные варианты сотрудничества"
    elif chance_score >= 40:
        return "СРЕДНИЕ ШАНСЫ: Уточните потребности, покажите экспертизу"
    elif chance_score >= 20:
        return "НИЗКИЕ ШАНСЫ: Попробуйте изменить подход или дайте время"
    else:
        return "ОЧЕНЬ НИЗКИЕ ШАНСЫ: Рассмотрите завершение диалога"

def print_analysis_results(analysis, messages):
    """Вывод результатов анализа"""
    
    print(f"\n📈 АНАЛИЗ ШАНСОВ НА ПРОЕКТ:")
    print(f"   Общая оценка: {analysis['project_chance_percent']}%")
    
    if analysis['project_chance_percent'] >= 70:
        emoji = "🟢"
    elif analysis['project_chance_percent'] >= 40:
        emoji = "🟡"
    else:
        emoji = "🔴"
    
    print(f"   Статус: {emoji} {get_status_text(analysis['project_chance_percent'])}")
    
    print(f"\n💬 СТАТИСТИКА ДИАЛОГА:")
    print(f"   Всего сообщений: {analysis['total_messages']}")
    print(f"   Ваших сообщений: {analysis['my_messages_count']}")
    print(f"   Их сообщений: {analysis['their_messages_count']}")
    print(f"   Коэффициент ответов: {analysis['response_ratio']:.2f}")
    print(f"   Длительность диалога: {analysis['conversation_duration_days']} дней")
    print(f"   Последняя активность: {analysis['last_activity_days']} дней назад")
    print(f"   Кто начал: {'Вы' if analysis['who_started'] == 'me' else 'Они'}")
    print(f"   Кто последний писал: {'Вы' if analysis['who_last_messaged'] == 'me' else 'Они'}")
    
    print(f"\n🔍 АНАЛИЗ СОДЕРЖАНИЯ:")
    print(f"   Упоминания проекта: {analysis['project_mentions']}")
    print(f"   Позитивные сигналы: {analysis['positive_signals']}")
    print(f"   Негативные сигналы: {analysis['negative_signals']}")
    print(f"   Сигналы срочности: {analysis['urgency_signals']}")
    
    print(f"\n💡 РЕКОМЕНДАЦИЯ:")
    print(f"   {analysis['recommendation']}")
    
    # Показываем последние сообщения
    print(f"\n📝 ПОСЛЕДНИЕ 5 СООБЩЕНИЙ:")
    print("=" * 50)
    
    for msg in messages[-5:]:
        direction = "→" if msg['is_outgoing'] else "←"
        date = msg['date'][:16] if msg['date'] else 'Unknown'
        text = msg['text'][:100] + '...' if len(msg['text']) > 100 else msg['text']
        print(f"[{date}] {direction} {text}")

def get_status_text(score):
    """Получить текстовое описание статуса"""
    if score >= 80:
        return "ОТЛИЧНЫЕ ШАНСЫ"
    elif score >= 60:
        return "ХОРОШИЕ ШАНСЫ"
    elif score >= 40:
        return "СРЕДНИЕ ШАНСЫ"
    elif score >= 20:
        return "НИЗКИЕ ШАНСЫ"
    else:
        return "ОЧЕНЬ НИЗКИЕ ШАНСЫ"

async def main():
    """Главная функция"""
    print("🔮 АНАЛИЗ ДИАЛОГА ДЛЯ ОЦЕНКИ ШАНСОВ НА ПРОЕКТ")
    print("="*60)
    
    result = await analyze_dialog_for_project()
    
    if result:
        print("\n✅ Анализ завершен успешно!")
        chance = result['analysis']['project_chance_percent']
        print(f"🎯 ИТОГОВАЯ ОЦЕНКА: {chance}% шансов получить проект")
    else:
        print("\n❌ Анализ не удался")

if __name__ == "__main__":
    asyncio.run(main())
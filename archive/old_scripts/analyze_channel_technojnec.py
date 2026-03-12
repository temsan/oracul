#!/usr/bin/env python3
"""
Анализ канала 2402063854 с помощью Oracul Engine
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append('oracul-bot')

try:
    from analyzers.channel_analyzer import ChannelAnalyzer
    from config.settings import settings
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что находитесь в корневой папке проекта")
    sys.exit(1)

async def analyze_channel_technojnec():
    """Анализ канала @technojnec"""
    
    print("🔮 Запуск анализа канала 2402063854...")
    
    analyzer = ChannelAnalyzer()
    
    try:
        # Инициализация клиента
        print("📡 Инициализация Telegram клиента...")
        
        # Получаем настройки из .env или используем дефолтные
        api_id = os.getenv('API_ID')
        api_hash = os.getenv('API_HASH') 
        phone = os.getenv('PHONE')
        
        if not api_id or not api_hash:
            print("❌ Не найдены API_ID или API_HASH в .env файле")
            return
            
        success = await analyzer.initialize_client(
            api_id=int(api_id),
            api_hash=api_hash,
            phone=phone
        )
        
        if not success:
            print("❌ Не удалось инициализировать Telegram клиент")
            return
            
        print("✅ Telegram клиент инициализирован")
        
        # Анализируем канал
        print(f"📊 Анализ канала 2402063854...")
        
        result = await analyzer.analyze_channel('2402063854', message_limit=100)
        
        # Выводим результаты
        print("\n" + "="*60)
        print("🎯 РЕЗУЛЬТАТ АНАЛИЗА КАНАЛА 2402063854")
        print("="*60)
        
        if result['success']:
            channel_info = result['channel_info']
            content_analysis = result.get('content_analysis', {})
            audience_analysis = result.get('audience_analysis', {})
            insights = result.get('insights', {})
            
            # Основная информация о канале
            print(f"\n📺 ИНФОРМАЦИЯ О КАНАЛЕ:")
            print(f"   Название: {channel_info.get('title', 'Не указано')}")
            print(f"   ID: {channel_info.get('id', 'Не указан')}")
            print(f"   Username: @{channel_info.get('username', 'Не указан')}")
            print(f"   Тип: {channel_info.get('type', 'Не указан')}")
            print(f"   Подписчиков: {channel_info.get('participants_count', 0):,}")
            print(f"   Верифицирован: {'Да' if channel_info.get('verified') else 'Нет'}")
            print(f"   Описание: {channel_info.get('description', 'Отсутствует')[:200]}...")
            
            # Статистика контента
            if 'statistics' in content_analysis:
                stats = content_analysis['statistics']
                print(f"\n📊 СТАТИСТИКА КОНТЕНТА:")
                print(f"   Проанализировано сообщений: {stats.get('total_messages', 0)}")
                print(f"   Общее количество символов: {stats.get('total_characters', 0):,}")
                print(f"   Общее количество слов: {stats.get('total_words', 0):,}")
                print(f"   Средняя длина сообщения: {stats.get('avg_message_length', 0):.1f} символов")
                
                # Вовлеченность
                if 'engagement_stats' in stats:
                    eng = stats['engagement_stats']
                    print(f"\n💬 ВОВЛЕЧЕННОСТЬ:")
                    print(f"   Общие просмотры: {eng.get('total_views', 0):,}")
                    print(f"   Общие репосты: {eng.get('total_forwards', 0):,}")
                    print(f"   Общие ответы: {eng.get('total_replies', 0):,}")
                    print(f"   Средние просмотры: {eng.get('avg_views', 0):.1f}")
                    print(f"   Коэффициент вовлеченности: {eng.get('engagement_rate', 0):.2f}%")
                
                # Распределение медиа
                if 'media_distribution' in stats:
                    media = stats['media_distribution']
                    print(f"\n🎨 ТИПЫ КОНТЕНТА:")
                    for media_type, data in media.items():
                        print(f"   {media_type}: {data['count']} ({data['percentage']:.1f}%)")
            
            # LLM анализ
            if 'llm_analysis' in content_analysis:
                llm = content_analysis['llm_analysis']
                print(f"\n🧠 AI АНАЛИЗ КОНТЕНТА:")
                print(f"   Основная тематика: {llm.get('main_topic', 'Не определена')}")
                print(f"   Целевая аудитория: {llm.get('target_audience', 'Не определена')}")
                print(f"   Стиль контента: {llm.get('content_style', 'Не определен')}")
                print(f"   Качество контента: {llm.get('content_quality', 'Не оценено')}/10")
                print(f"   Потенциал монетизации: {llm.get('monetization_potential', 'Не определен')}")
                print(f"   Категория: {llm.get('channel_category', 'Не определена')}")
                
                if 'recommendations' in llm and llm['recommendations']:
                    print(f"\n💡 РЕКОМЕНДАЦИИ:")
                    for i, rec in enumerate(llm['recommendations'][:5], 1):
                        print(f"   {i}. {rec}")
            
            # Анализ тем
            if 'topics' in content_analysis:
                topics = content_analysis['topics']
                if 'categories' in topics:
                    print(f"\n🏷️ КАТЕГОРИИ КОНТЕНТА:")
                    for category, count in topics['categories'].items():
                        if count > 0:
                            print(f"   {category}: {count} упоминаний")
                
                if 'top_words' in topics and topics['top_words']:
                    print(f"\n🔤 ТОП СЛОВА:")
                    for word, count in topics['top_words'][:10]:
                        print(f"   {word}: {count}")
            
            # Инсайты
            if insights:
                print(f"\n🎯 ИНСАЙТЫ:")
                if 'channel_assessment' in insights:
                    assessment = insights['channel_assessment']
                    for key, value in assessment.items():
                        print(f"   {key}: {value}")
                
                if 'growth_potential' in insights:
                    growth = insights['growth_potential']
                    for key, value in growth.items():
                        print(f"   Потенциал {key}: {value}")
            
            # Сохраняем результат в файл
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis/channel_technojnec_analysis_{timestamp}.json"
            
            os.makedirs("analysis", exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 Результат сохранен в: {filename}")
            
        else:
            print(f"❌ ОШИБКА АНАЛИЗА: {result.get('error', 'Неизвестная ошибка')}")
            
        await analyzer.close()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Запуск анализа
    asyncio.run(analyze_channel_technojnec())
#!/usr/bin/env python3
"""
Анализ чата 1637334 с современными моделями
Использует интегрированный анализатор (локальные + OpenRouter)
"""

import asyncio
import sys
import os
import json
from pathlib import Path
import logging
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / 'oracul-bot'))

from analyzers.local_text_analyzer import LocalTextAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Chat1637334ModernAnalysis:
    """Анализ чата 1637334 с современными моделями"""
    
    def __init__(self):
        self.analyzer = None
        self.chat_id = 1637334
    
    async def initialize(self):
        """Инициализация анализатора"""
        try:
            print("🚀 Инициализация интегрированного анализатора...")
            
            # Проверяем настройки
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            if openrouter_key:
                print(f"🔑 OpenRouter API ключ: {openrouter_key[:20]}...")
            else:
                print("⚠️ OpenRouter API ключ не найден")
            
            # Инициализируем анализатор
            self.analyzer = LocalTextAnalyzer()
            
            print("✅ Инициализация завершена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    def get_sample_messages(self):
        """Получить образцы сообщений для анализа (имитация реальных данных)"""
        # Это образцы сообщений в стиле чата 1637334
        return [
            {
                'id': 1,
                'text': 'Привет! Как дела? Сегодня отличный день для работы над проектом.',
                'date': '2024-12-30T10:00:00',
                'type': 'positive_greeting'
            },
            {
                'id': 2,
                'text': 'Работаю над новой архитектурой нейронной сети. Пока что результаты не очень, но не сдаюсь.',
                'date': '2024-12-30T11:30:00',
                'type': 'technical_mixed'
            },
            {
                'id': 3,
                'text': 'Немного устал от отладки. Ошибки появляются одна за другой, но это нормальный процесс разработки.',
                'date': '2024-12-30T14:15:00',
                'type': 'frustrated_realistic'
            },
            {
                'id': 4,
                'text': 'Наконец-то прорыв! Модель начала показывать хорошие результаты. Очень доволен прогрессом.',
                'date': '2024-12-30T16:45:00',
                'type': 'breakthrough_joy'
            },
            {
                'id': 5,
                'text': 'Размышляю о будущем AI и его влиянии на общество. Технологии развиваются быстро, но важно помнить об этике.',
                'date': '2024-12-30T18:20:00',
                'type': 'philosophical_reflection'
            },
            {
                'id': 6,
                'text': 'Завтра планирую протестировать новые алгоритмы. Надеюсь, что все пройдет гладко.',
                'date': '2024-12-30T19:00:00',
                'type': 'planning_hopeful'
            }
        ]
    
    async def analyze_messages(self, messages, use_modern=True):
        """Анализ сообщений с современными моделями"""
        try:
            print(f"\n🧠 АНАЛИЗ СООБЩЕНИЙ ЧАТА {self.chat_id}")
            print("=" * 60)
            
            analyses = []
            
            for i, message in enumerate(messages, 1):
                print(f"\n--- Сообщение {i}/{len(messages)}: {message['type']} ---")
                print(f"📝 Текст: {message['text'][:80]}...")
                print(f"🕒 Дата: {message['date']}")
                
                try:
                    # Анализируем с современными моделями
                    result = await self.analyzer.analyze(
                        message['text'], 
                        use_modern=use_modern
                    )
                    
                    if result.get('success'):
                        print("✅ Анализ успешен")
                        
                        # Локальные результаты
                        sentiment = result.get('sentiment', {})
                        if sentiment:
                            print(f"  🧠 Локальная тональность: {sentiment.get('label')} ({sentiment.get('confidence', 0)*100:.1f}%)")
                        
                        emotions = result.get('emotions', {})
                        if emotions:
                            top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
                            emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_emotions if s > 0.1])
                            if emotion_str:
                                print(f"  😊 Локальные эмоции: {emotion_str}")
                        
                        # Современные результаты
                        modern_analysis = result.get('modern_analysis', {})
                        if modern_analysis and modern_analysis.get('success'):
                            print(f"  🤖 Современная модель: {modern_analysis.get('model_used', 'unknown')}")
                            
                            openrouter_data = modern_analysis.get('openrouter_analysis', {})
                            
                            if 'sentiment' in openrouter_data:
                                or_sent = openrouter_data['sentiment']
                                print(f"  📊 OpenRouter тональность: {or_sent.get('label')} ({or_sent.get('confidence', 0)*100:.1f}%)")
                            
                            if 'emotions' in openrouter_data:
                                or_emotions = openrouter_data['emotions']
                                if isinstance(or_emotions, dict):
                                    top_or_emotions = sorted(or_emotions.items(), key=lambda x: x[1], reverse=True)[:2]
                                    or_emotion_str = ', '.join([f"{e}: {s*100:.1f}%" for e, s in top_or_emotions if s > 0.1])
                                    if or_emotion_str:
                                        print(f"  🤖 OpenRouter эмоции: {or_emotion_str}")
                            
                            if 'insights' in openrouter_data:
                                insights = openrouter_data['insights']
                                if isinstance(insights, list) and insights:
                                    print(f"  💡 Инсайты: {'; '.join(insights[:2])}")
                        
                        # Методы анализа
                        methods = result.get('analysis_methods', [])
                        print(f"  🔧 Методы: {', '.join(methods)}")
                        
                        analyses.append({
                            'message_id': message['id'],
                            'message_type': message['type'],
                            'text': message['text'],
                            'date': message['date'],
                            'analysis': result,
                            'success': True
                        })
                        
                    else:
                        print(f"❌ Ошибка анализа: {result.get('error')}")
                        analyses.append({
                            'message_id': message['id'],
                            'message_type': message['type'],
                            'text': message['text'],
                            'date': message['date'],
                            'error': result.get('error'),
                            'success': False
                        })
                        
                except Exception as e:
                    print(f"❌ Критическая ошибка: {e}")
                    analyses.append({
                        'message_id': message['id'],
                        'message_type': message['type'],
                        'text': message['text'],
                        'date': message['date'],
                        'error': str(e),
                        'success': False
                    })
            
            return analyses
            
        except Exception as e:
            print(f"❌ Ошибка анализа сообщений: {e}")
            return []
    
    def generate_comprehensive_report(self, analyses):
        """Генерация комплексного отчета"""
        try:
            print(f"\n📊 КОМПЛЕКСНЫЙ ОТЧЕТ АНАЛИЗА ЧАТА {self.chat_id}")
            print("=" * 70)
            
            # Статистика успешности
            successful = [a for a in analyses if a.get('success')]
            total = len(analyses)
            success_rate = len(successful) / total * 100 if total > 0 else 0
            
            print(f"📈 ОБЩАЯ СТАТИСТИКА:")
            print(f"  • Всего сообщений: {total}")
            print(f"  • Успешно проанализировано: {len(successful)}")
            print(f"  • Успешность: {success_rate:.1f}%")
            
            if not successful:
                print("⚠️ Нет успешных анализов для генерации отчета")
                return {}
            
            # Анализ тональности
            local_sentiments = []
            modern_sentiments = []
            methods_used = set()
            
            for analysis in successful:
                result = analysis['analysis']
                
                # Локальная тональность
                sentiment = result.get('sentiment', {})
                if sentiment.get('label'):
                    local_sentiments.append(sentiment['label'])
                
                # Современная тональность
                modern_analysis = result.get('modern_analysis', {})
                if modern_analysis and modern_analysis.get('success'):
                    openrouter_data = modern_analysis.get('openrouter_analysis', {})
                    if 'sentiment' in openrouter_data:
                        modern_sentiments.append(openrouter_data['sentiment']['label'])
                
                # Методы
                methods = result.get('analysis_methods', [])
                methods_used.update(methods)
            
            # Статистика тональности
            print(f"\n📊 АНАЛИЗ ТОНАЛЬНОСТИ:")
            
            if local_sentiments:
                local_counts = {}
                for s in local_sentiments:
                    local_counts[s] = local_counts.get(s, 0) + 1
                
                print(f"  🧠 Локальные модели:")
                for sentiment, count in sorted(local_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(local_sentiments) * 100
                    print(f"    - {sentiment}: {count} ({percentage:.1f}%)")
            
            if modern_sentiments:
                modern_counts = {}
                for s in modern_sentiments:
                    modern_counts[s] = modern_counts.get(s, 0) + 1
                
                print(f"  🤖 Современные модели (OpenRouter):")
                for sentiment, count in sorted(modern_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(modern_sentiments) * 100
                    print(f"    - {sentiment}: {count} ({percentage:.1f}%)")
            
            # Сравнение методов
            print(f"\n🔧 ИСПОЛЬЗОВАННЫЕ МЕТОДЫ:")
            for method in sorted(methods_used):
                method_count = sum(1 for a in successful if method in a['analysis'].get('analysis_methods', []))
                percentage = method_count / len(successful) * 100
                print(f"  • {method}: {method_count}/{len(successful)} ({percentage:.1f}%)")
            
            # Качественные инсайты
            print(f"\n💡 КЛЮЧЕВЫЕ ИНСАЙТЫ:")
            
            # Анализ по типам сообщений
            message_types = {}
            for analysis in successful:
                msg_type = analysis.get('message_type', 'unknown')
                if msg_type not in message_types:
                    message_types[msg_type] = []
                
                result = analysis['analysis']
                sentiment = result.get('sentiment', {})
                if sentiment.get('label'):
                    message_types[msg_type].append(sentiment['label'])
            
            for msg_type, sentiments in message_types.items():
                if sentiments:
                    dominant = max(set(sentiments), key=sentiments.count)
                    print(f"  • {msg_type}: доминирующая тональность - {dominant}")
            
            # Эффективность современных моделей
            modern_available = sum(1 for a in successful if 'openrouter_api' in a['analysis'].get('analysis_methods', []))
            if modern_available > 0:
                modern_rate = modern_available / len(successful) * 100
                print(f"  • Современные модели доступны в {modern_rate:.1f}% случаев")
                print(f"  • Интегрированный анализ работает стабильно")
            else:
                print(f"  • Современные модели недоступны (проверьте API ключ)")
            
            # Генерируем итоговый отчет
            report = {
                'chat_id': self.chat_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'total_messages': total,
                'successful_analyses': len(successful),
                'success_rate': success_rate,
                'local_sentiment_distribution': local_counts if local_sentiments else {},
                'modern_sentiment_distribution': modern_counts if modern_sentiments else {},
                'methods_used': list(methods_used),
                'modern_models_availability': modern_rate if modern_available > 0 else 0,
                'message_type_analysis': message_types,
                'detailed_analyses': analyses
            }
            
            return report
            
        except Exception as e:
            print(f"❌ Ошибка генерации отчета: {e}")
            return {}
    
    async def save_report(self, report, filename=None):
        """Сохранение отчета"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis/chat_{self.chat_id}_modern_analysis_{timestamp}.json"
            
            # Создаем директорию если нужно
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 Отчет сохранен: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")
            return None


async def main():
    """Главная функция анализа чата 1637334"""
    print("🔮 АНАЛИЗ ЧАТА 1637334 С СОВРЕМЕННЫМИ AI-МОДЕЛЯМИ")
    print("🤖 Интегрированный анализ: Локальные + OpenRouter")
    print("=" * 70)
    
    analyzer = Chat1637334ModernAnalysis()
    
    try:
        # Инициализация
        if not await analyzer.initialize():
            print("❌ Ошибка инициализации")
            return
        
        # Получаем образцы сообщений
        print("\n📥 Получение сообщений для анализа...")
        messages = analyzer.get_sample_messages()
        print(f"✅ Получено {len(messages)} сообщений для анализа")
        
        # Анализ с современными моделями
        print("\n🔮 Запуск интегрированного анализа...")
        analyses = await analyzer.analyze_messages(messages, use_modern=True)
        
        # Генерация отчета
        print("\n📊 Генерация комплексного отчета...")
        report = analyzer.generate_comprehensive_report(analyses)
        
        if report:
            # Сохранение отчета
            filename = await analyzer.save_report(report)
            
            # Итоги
            print(f"\n🎯 АНАЛИЗ ЧАТА {analyzer.chat_id} ЗАВЕРШЕН!")
            print(f"📈 Успешность: {report.get('success_rate', 0):.1f}%")
            print(f"🔧 Методы: {', '.join(report.get('methods_used', []))}")
            print(f"🤖 Современные модели: {report.get('modern_models_availability', 0):.1f}% доступность")
            
            if filename:
                print(f"💾 Результаты сохранены в: {filename}")
        else:
            print("❌ Ошибка генерации отчета")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
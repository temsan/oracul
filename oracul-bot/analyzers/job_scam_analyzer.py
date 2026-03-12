"""
Анализатор мошеннических вакансий для Oracul Bot
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


class JobScamAnalyzer:
    """Детектор мошеннических вакансий"""
    
    # Признаки мошенничества с весами
    SCAM_INDICATORS = {
        'payment_request': {
            'patterns': [
                r'оплат[аи]\w*\s+(?:вывод|регистрац|обучен|курс|доступ)',
                r'перевед[иь]\w*\s+(?:сначала|деньги)',
                r'внести\s+(?:взнос|оплату)',
                r'приобрест[иь]\w*\s+(?:курс|доступ|браузер)'
            ],
            'description': '💰 Запрос на оплату',
            'weight': 10
        },
        'fake_guarantees': {
            'patterns': [
                r'система\s+безопасных\s+сделок',
                r'гарант\w*\s+(?:сделк|оплат)',
                r'через\s+гаранта'
            ],
            'description': '🛡️ Фейковые гарантии',
            'weight': 8
        },
        'suspicious_salary': {
            'patterns': [
                r'(?:от\s*)?(\d{2,3})\s*(?:тыс|тр|к)\s*руб',
                r'(?:зп|зарплата|оклад)\s*(\d{2,3})',
            ],
            'description': '💸 Завышенная зарплата',
            'threshold': 60,
            'weight': 3
        },
        'vague_company': {
            'patterns': [
                r'(?:дружный|профессиональный)\s+коллектив',
                r'возможност[иь]\s+(?:для\s+)?обучения',
                r'конкурентоспособная\s+зарплата'
            ],
            'description': '🏢 Нет названия компании',
            'weight': 3
        },
        'contact_via_dm': {
            'patterns': [
                r'@\w+',
                r'писать\s+в\s+(?:лс|личку|директ)',
                r'контакт[:\s]+@'
            ],
            'description': '📱 Контакт только через ЛС',
            'weight': 2
        },
        'suspicious_requirements': {
            'patterns': [
                r'рассматриваем\s+(?:только|кандидатов)\s+из\s+рф',
                r'только\s+из\s+(?:рф|россии)',
                r'специальн\w+\s+(?:карт|браузер|приложение)'
            ],
            'description': '⚠️ Подозрительные требования',
            'weight': 2
        },
        'too_good_to_be_true': {
            'patterns': [
                r'без\s+опыта',
                r'легк[ао]\w*\s+(?:работ|заработ)',
                r'гарантирован\w+\s+(?:заказ|доход)',
                r'куча\s+заказов'
            ],
            'description': '✨ Слишком хорошо',
            'weight': 3
        },
        'generic_tasks': {
            'patterns': [
                r'различн\w+\s+тип\w+\s+текстов',
                r'работа\s+с\s+(?:различными|разными)\s+текстами',
                r'технические,\s+юридические,\s+медицинские'
            ],
            'description': '📋 Общие задачи без конкретики',
            'weight': 2
        },
        'screen_sharing_request': {
            'patterns': [
                r'расшар\w+\s+экран',
                r'показ\w+\s+экран',
                r'демонстрац\w+\s+экран',
                r'трансляц\w+\s+экран',
                r'screen\s*shar',
                r'видеозвон\w+.*экран',
                r'звон\w+.*экран',
                r'включ\w+\s+запис'
            ],
            'description': '🎥 Запрос на демонстрацию экрана',
            'weight': 8  # Высокий вес - это критический признак
        },
        'video_call_mention': {
            'patterns': [
                r'видеозвон',
                r'видео\s*звон',
                r'видео\s*связ',
                r'видео\s*собеседован',
                r'zoom.*собеседован',
                r'skype.*собеседован'
            ],
            'description': '📹 Упоминание видеозвонка',
            'weight': 1  # Низкий вес - само по себе не подозрительно
        }
    }
    
    @classmethod
    def analyze(cls, text: str, sender_id: int = None) -> Dict:
        """
        Анализ текста вакансии на признаки мошенничества
        
        Args:
            text: Текст вакансии
            sender_id: ID отправителя (опционально)
            
        Returns:
            Dict с результатами анализа
        """
        scam_score = 0
        found_indicators = []
        
        text_lower = text.lower()
        
        # Проверяем каждый индикатор
        for indicator_name, indicator_data in cls.SCAM_INDICATORS.items():
            patterns = indicator_data.get('patterns', [])
            weight = indicator_data.get('weight', 1)
            description = indicator_data.get('description', indicator_name)
            
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                if found:
                    matches.extend(found)
            
            if matches:
                # Специальная обработка для зарплаты
                if indicator_name == 'suspicious_salary':
                    salaries = []
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        try:
                            salary = int(match)
                            salaries.append(salary)
                        except:
                            pass
                    
                    if salaries and max(salaries) > indicator_data['threshold']:
                        scam_score += weight
                        found_indicators.append({
                            'type': indicator_name,
                            'description': f"{description} ({max(salaries)}K > {indicator_data['threshold']}K)",
                            'weight': weight
                        })
                else:
                    scam_score += weight
                    found_indicators.append({
                        'type': indicator_name,
                        'description': description,
                        'weight': weight
                    })
        
        # Анализ отправителя (если ID предоставлен)
        if sender_id:
            account_score = cls._analyze_sender_id(sender_id)
            if account_score > 0:
                scam_score += account_score
                found_indicators.append({
                    'type': 'new_account',
                    'description': f'🆕 Новый аккаунт (ID: {sender_id})',
                    'weight': account_score
                })
        
        # Определяем уровень риска
        risk_level, recommendation = cls._get_risk_level(scam_score)
        
        return {
            'scam_score': scam_score,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'indicators': found_indicators,
            'total_indicators': len(found_indicators),
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def _analyze_sender_id(sender_id: int) -> int:
        """Анализ ID отправителя на подозрительность"""
        if sender_id > 8000000000:
            return 5  # Очень новый аккаунт
        elif sender_id > 5000000000:
            return 3  # Новый аккаунт
        elif sender_id > 1000000000:
            return 1  # Относительно новый
        return 0
    
    @staticmethod
    def _get_risk_level(score: int) -> Tuple[str, str]:
        """Определение уровня риска по баллам"""
        if score >= 15:
            return (
                '🔴 ВЫСОКИЙ РИСК',
                'НЕ ОТКЛИКАЙТЕСЬ! Множественные признаки мошенничества.'
            )
        elif score >= 8:
            return (
                '🟠 СРЕДНИЙ РИСК',
                'Будьте осторожны. Тщательно проверьте компанию.'
            )
        elif score >= 4:
            return (
                '🟡 НИЗКИЙ РИСК',
                'Проверьте название компании и отзывы.'
            )
        else:
            return (
                '🟢 МИНИМАЛЬНЫЙ РИСК',
                'Вакансия выглядит легитимно, но проверяйте детали.'
            )
    
    @classmethod
    def format_report(cls, analysis: Dict, include_details: bool = True) -> str:
        """
        Форматирование отчета для Telegram
        
        Args:
            analysis: Результаты анализа
            include_details: Включать ли детали индикаторов
            
        Returns:
            Отформатированный текст отчета
        """
        report = "🚨 *ПРОВЕРКА ВАКАНСИИ НА МОШЕННИЧЕСТВО*\n\n"
        
        # Вердикт
        report += f"*Уровень риска:* {analysis['risk_level']}\n"
        report += f"*Баллов:* {analysis['scam_score']}\n\n"
        report += f"💡 *Рекомендация:*\n{analysis['recommendation']}\n"
        
        # Найденные индикаторы
        if analysis['indicators'] and include_details:
            report += f"\n⚠️ *Найдено признаков:* {analysis['total_indicators']}\n\n"
            for indicator in analysis['indicators']:
                report += f"• {indicator['description']} (+{indicator['weight']})\n"
        
        # Дополнительная информация
        if analysis['scam_score'] >= 8:
            report += "\n🛡️ *Как защититься:*\n"
            report += "• Не переводите деньги\n"
            report += "• Не скачивайте приложения\n"
            report += "• Проверьте компанию в Google\n"
            report += "• Ищите отзывы о работодателе\n"
        
        return report
    
    @classmethod
    def quick_check(cls, text: str) -> str:
        """
        Быстрая проверка с кратким ответом
        
        Args:
            text: Текст вакансии
            
        Returns:
            Краткий вердикт
        """
        analysis = cls.analyze(text)
        
        emoji_map = {
            '🔴 ВЫСОКИЙ РИСК': '🔴',
            '🟠 СРЕДНИЙ РИСК': '🟠',
            '🟡 НИЗКИЙ РИСК': '🟡',
            '🟢 МИНИМАЛЬНЫЙ РИСК': '🟢'
        }
        
        emoji = emoji_map.get(analysis['risk_level'], '❓')
        
        return (
            f"{emoji} *{analysis['risk_level']}* "
            f"({analysis['scam_score']} баллов)\n"
            f"{analysis['recommendation']}"
        )


# Пример использования
if __name__ == "__main__":
    test_text = """
    Требуется редактор публикаций
    Оклад 68 тр +бонусная программа
    Дружный и профессиональный коллектив
    Контакт: @margo_antipovaa
    Рассматриваем кандидатов только из рф
    """
    
    analyzer = JobScamAnalyzer()
    result = analyzer.analyze(test_text, sender_id=8345148786)
    
    print(analyzer.format_report(result))
    print("\n" + "="*60 + "\n")
    print(analyzer.quick_check(test_text))

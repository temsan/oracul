# 🚨 Детектор мошеннических вакансий - Навигация

Быстрый доступ ко всем материалам.

---

## 🚀 Быстрый старт

### Проверить вакансию прямо сейчас:

```bash
python scripts/career_job_search/scam_detection/check_job_scam.py
```

---

## 📚 Документация

| Документ | Описание | Ссылка |
|----------|----------|--------|
| 📖 Руководство | Полное руководство пользователя | [SCAM_DETECTOR_GUIDE.md](SCAM_DETECTOR_GUIDE.md) |
| ⚡ Быстрый старт | Начните за 1 минуту | [QUICK_SCAM_CHECK.md](QUICK_SCAM_CHECK.md) |
| 🔧 Интеграция | Добавьте в Oracul Bot | [SCAM_DETECTOR_INTEGRATION.md](SCAM_DETECTOR_INTEGRATION.md) |
| 📊 Сводка | Краткая информация | [SCAM_DETECTOR_SUMMARY.md](SCAM_DETECTOR_SUMMARY.md) |

---

## 🔧 Инструменты

| Скрипт | Назначение | Команда |
|--------|-----------|---------|
| check_job_scam.py | Быстрая проверка текста | `python scripts/career_job_search/scam_detection/check_job_scam.py` |
| check_specific_job.py | Проверка по ссылке | `python scripts/career_job_search/scam_detection/check_specific_job.py` |
| find_scam_network.py | Поиск сети мошенников | `python scripts/career_job_search/scam_detection/find_scam_network.py` |
| detect_job_scam.py | Полный анализ с примером | `python scripts/career_job_search/scam_detection/detect_job_scam.py` |

**Расположение:** `scripts/career_job_search/scam_detection/`

---

## 📊 Отчеты

| Тип | Описание | Расположение |
|-----|----------|--------------|
| Детальные | Глубокий анализ вакансий | `analysis/career_development/scam_reports/detailed/` |
| По ссылкам | Анализ конкретных вакансий | `analysis/career_development/scam_reports/job_scam_analysis_*.md` |
| Сеть | Анализ мошеннической сети | `analysis/career_development/scam_reports/scam_network_*.md` |

**Главный README:** `analysis/career_development/scam_reports/README.md`

---

## 🤖 Интеграция с ботом

| Модуль | Назначение | Расположение |
|--------|-----------|--------------|
| job_scam_analyzer.py | Ядро анализатора | `oracul-bot/analyzers/` |
| job_scam_handler.py | Обработчики команд | `oracul-bot/bot/` |

**Команда в боте:** `/checkjob`

---

## 🎯 Ваши вакансии

### 1. @margo_antipovaa
- **Риск:** 🔴 ВЫСОКИЙ (17 баллов)
- **Вердикт:** МОШЕННИЧЕСТВО
- **Отчет:** [scam_analysis_margo_antipovaa.md](../../analysis/career_development/scam_reports/detailed/scam_analysis_margo_antipovaa.md)

### 2. @Hr_Veronika3
- **Риск:** 🟠 СРЕДНИЙ (12 баллов)
- **Вердикт:** ПОДОЗРИТЕЛЬНО
- **Ссылка:** https://t.me/TRemoters/7752
- **Отчет:** [job_scam_analysis_20260115_144218.md](../../analysis/career_development/scam_reports/job_scam_analysis_20260115_144218.md)

---

## 📈 Признаки мошенничества

### Уровни риска:

| Баллы | Уровень | Эмодзи | Действие |
|-------|---------|--------|----------|
| 15+ | ВЫСОКИЙ | 🔴 | НЕ откликайтесь |
| 8-14 | СРЕДНИЙ | 🟠 | Будьте осторожны |
| 4-7 | НИЗКИЙ | 🟡 | Требует проверки |
| 0-3 | МИНИМАЛЬНЫЙ | 🟢 | Можно откликаться |

### Индикаторы:

| Признак | Вес | Описание |
|---------|-----|----------|
| 💰 Запрос оплаты | 10 | Просят оплатить обучение/регистрацию |
| 🛡️ Фейковые гарантии | 8 | "Система безопасных сделок" |
| 🆕 Новый аккаунт | 5 | ID > 5 млрд |
| 💸 Завышенная зарплата | 3 | Выше рынка на 30%+ |
| 🏢 Нет компании | 3 | Размытые формулировки |
| 📱 Только ЛС | 2 | Контакт через личку |
| ⚠️ Странные требования | 2 | "Только из РФ", спец. карта |
| ✨ Слишком хорошо | 3 | "Без опыта", "гарантированный доход" |
| 📋 Общие задачи | 2 | "Различные типы текстов" |

---

## 🛡️ Как защититься

### ❌ НИКОГДА:
- Не переводите деньги
- Не скачивайте подозрительные приложения
- Не показывайте экран с кодами
- Не вводите данные карты на незнакомых сайтах

### ✅ ВСЕГДА:
- Проверяйте название компании
- Ищите отзывы о работодателе
- Используйте детектор перед откликом
- Сравнивайте зарплату с рынком

---

## 📞 Контакты

**Вопросы:** @temsanone  
**Email:** temsanone@gmail.com

---

## 🔗 Полезные ссылки

- [Финальный отчет](../../SCAM_DETECTOR_FINAL_REPORT.md)
- [README скриптов](../../scripts/career_job_search/scam_detection/README.md)
- [README отчетов](../../analysis/career_development/scam_reports/README.md)

---

**Последнее обновление:** 2026-01-15

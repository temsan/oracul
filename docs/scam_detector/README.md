# 🚨 Детектор мошеннических вакансий

Полная система для выявления и защиты от мошенничества при поиске работы в Telegram.

---

## 🚀 Быстрый старт

```bash
python scripts/career_job_search/scam_detection/check_job_scam.py
```

Вставьте текст вакансии → Получите анализ за секунды.

---

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [INDEX.md](INDEX.md) | 📑 Навигация по всем материалам |
| [QUICK_SCAM_CHECK.md](QUICK_SCAM_CHECK.md) | ⚡ Быстрый старт за 1 минуту |
| [SCAM_DETECTOR_GUIDE.md](SCAM_DETECTOR_GUIDE.md) | 📖 Полное руководство пользователя |
| [SCAM_DETECTOR_INTEGRATION.md](SCAM_DETECTOR_INTEGRATION.md) | 🔧 Интеграция с Oracul Bot |
| [SCAM_DETECTOR_SUMMARY.md](SCAM_DETECTOR_SUMMARY.md) | 📊 Краткая сводка |
| [SCREEN_SHARING_SCAM.md](SCREEN_SHARING_SCAM.md) | 🎥 Схема с расшариванием экрана |
| [SCAM_INDICATORS_UPDATE.md](SCAM_INDICATORS_UPDATE.md) | 🆕 Новые индикаторы v1.1 |
| [SCAM_DETECTOR_COMPLETE.md](SCAM_DETECTOR_COMPLETE.md) | ✅ Полный отчет о системе |
| [SCAM_DETECTOR_FINAL_REPORT.md](SCAM_DETECTOR_FINAL_REPORT.md) | 📋 Финальный отчет |
| [SCAM_DETECTOR_UPDATE_v1.1.md](SCAM_DETECTOR_UPDATE_v1.1.md) | 🆕 Обновление v1.1 |

---

## 🎯 Ваши вакансии

### 1. @margo_antipovaa (ID: 8345148786)
- **Риск:** 🔴 ВЫСОКИЙ (17 баллов)
- **Вердикт:** МОШЕННИЧЕСТВО
- **Действие:** НЕ откликайтесь!

### 2. @Hr_Veronika3
- **Риск:** 🟠 СРЕДНИЙ (12 баллов)
- **Вердикт:** ПОДОЗРИТЕЛЬНО
- **Ссылка:** https://t.me/TRemoters/7752

**Вывод:** Организованная мошенническая сеть.

---

## 🛡️ Что проверяет детектор

### Критические (10+ баллов):
- 💰 Запросы на оплату
- 🛡️ Фейковые гарантии
- 🎥 Расшаривание экрана ← v1.1

### Высокий риск (5-8 баллов):
- 🆕 Новый аккаунт
- 💸 Завышенная зарплата

### Средний риск (2-3 балла):
- 📱 Контакт только через ЛС
- 🏢 Нет названия компании
- ⚠️ Подозрительные требования
- ✨ "Слишком хорошо"
- 📋 Общие задачи

### Низкий риск (1 балл):
- 📹 Видеозвонок ← v1.1

---

## 🔧 Инструменты

Все скрипты в `scripts/career_job_search/scam_detection/`:

- `check_job_scam.py` - Быстрая интерактивная проверка
- `check_specific_job.py` - Проверка по ссылке Telegram
- `find_scam_network.py` - Поиск сети мошенников
- `detect_job_scam.py` - Полный анализ с примером
- `test_screen_sharing_scam.py` - Тесты новых индикаторов

---

## 🤖 Интеграция с ботом

Модули в `oracul-bot/`:

- `analyzers/job_scam_analyzer.py` - Ядро анализатора (v1.1)
- `bot/job_scam_handler.py` - Команда `/checkjob`

---

## 📊 Отчеты

Все отчеты в `analysis/career_development/scam_reports/`:

- `detailed/` - Детальные анализы
- `job_scam_analysis_*.md` - Анализ по ссылкам
- `scam_network_report_*.md` - Анализ сети

---

## 📈 Версии

### v1.1 (2026-01-15)
- ✅ Добавлена защита от расшаривания экрана
- ✅ 2 новых индикатора
- ✅ 14 новых паттернов
- ✅ Документация о схеме

### v1.0 (2026-01-15)
- ✅ Первый релиз
- ✅ 9 индикаторов мошенничества
- ✅ 4 скрипта
- ✅ Интеграция с ботом
- ✅ Полная документация

---

## 📞 Контакты

**Вопросы:** @temsanone  
**Email:** temsanone@gmail.com

---

**Система готова к использованию. Будьте защищены!** 🛡️

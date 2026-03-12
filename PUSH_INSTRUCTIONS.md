# 🚀 Инструкции по отправке очищенной истории

## ✅ Что сделано:

1. ✅ Файл `archive/old_docs/CLIPROXYAPI_README.md` удален из всей истории Git
2. ✅ Секреты больше не присутствуют в локальной истории
3. ✅ Создан бэкап: `../oracul-backup-mirror.git`
4. ✅ Рефлоги очищены
5. ✅ Выполнена сборка мусора

## 🔴 КРИТИЧЕСКИ ВАЖНО: Ротация ключей

**ПЕРЕД отправкой на GitHub, ротируйте ВСЕ ключи:**

### 1. OpenRouter API Key
```bash
# Старый ключ (СКОМПРОМЕТИРОВАН):
sk-or-v1-[REDACTED]

# Действия:
# 1. Зайдите: https://openrouter.ai/keys
# 2. Удалите старый ключ
# 3. Создайте новый
# 4. Обновите .env
```

### 2. GROQ API Key
```bash
# Старый ключ (СКОМПРОМЕТИРОВАН):
gsk_[REDACTED]

# Действия:
# 1. Зайдите: https://console.groq.com/keys
# 2. Удалите старый ключ
# 3. Создайте новый
# 4. Обновите .env
```

### 3. Telegram Bot Token
```bash
# Старый токен (СКОМПРОМЕТИРОВАН):
[REDACTED]

# Действия:
# 1. Откройте @BotFather в Telegram
# 2. Отправьте: /revoke
# 3. Выберите вашего бота
# 4. Получите новый токен
# 5. Обновите .env
```

### 4. Telegram API Credentials
```bash
# Старые данные (СКОМПРОМЕТИРОВАНЫ):
TG_API_ID=[REDACTED]
TG_API_HASH=[REDACTED]

# Действия:
# 1. Зайдите: https://my.telegram.org/apps
# 2. Удалите старое приложение
# 3. Создайте новое
# 4. Обновите TG_API_ID и TG_API_HASH в .env
```

### 5. Gemini API Key (CLIProxyAPI)
```bash
# Старый ключ (СКОМПРОМЕТИРОВАН):
AIzaSy[REDACTED]

# Действия:
# 1. Зайдите: https://makersuite.google.com/app/apikey
# 2. Удалите старый ключ
# 3. Создайте новый
# 4. Обновите конфигурацию
```

---

## 🚀 Отправка на GitHub

**ТОЛЬКО после ротации всех ключей выше!**

```bash
# 1. Проверьте текущее состояние
git status
git log --oneline -10

# 2. Force push (ПЕРЕЗАПИШЕТ историю на GitHub!)
git push origin --force --all

# 3. Force push тегов (если есть)
git push origin --force --tags

# 4. Проверьте на GitHub
# Откройте: https://github.com/temsan/oracul/commits/master
# Убедитесь что старые коммиты с секретами исчезли
```

---

## ⚠️ Важные предупреждения

### Для других разработчиков:
После force push все, кто клонировал репозиторий, должны выполнить:

```bash
cd oracul
git fetch origin
git reset --hard origin/master
git clean -fdx
```

### GitHub кэширование:
- GitHub может кэшировать старые коммиты до 90 дней
- Старые коммиты могут быть доступны по прямой ссылке
- Рассмотрите возможность сделать репозиторий приватным на время

### Проверка после push:
```bash
# Проверьте что секреты не видны на GitHub
# 1. Откройте историю коммитов
# 2. Попробуйте найти старые коммиты: fe86bcae, 091750a
# 3. Они должны быть недоступны или без секретов
```

---

## 📋 Чеклист перед push

- [ ] ✅ Ротирован OpenRouter API Key
- [ ] ✅ Ротирован GROQ API Key  
- [ ] ✅ Ротирован Telegram Bot Token
- [ ] ✅ Ротированы Telegram API credentials (ID + Hash)
- [ ] ✅ Ротирован Gemini API Key
- [ ] ✅ Обновлен файл `.env` с новыми ключами
- [ ] ✅ Проверена работа бота с новыми ключами
- [ ] ⏳ Выполнен `git push origin --force --all`
- [ ] ⏳ Проверено на GitHub что секреты исчезли

---

## 🔄 Восстановление из бэкапа (если нужно)

Если что-то пошло не так:

```bash
# Вернитесь к бэкапу
cd ..
git clone oracul-backup-mirror.git oracul-restored
cd oracul-restored

# Или восстановите текущий репозиторий
cd oracul
git remote add backup ../oracul-backup-mirror.git
git fetch backup
git reset --hard backup/master
```

---

## 📞 Поддержка

Если возникли проблемы:
1. НЕ делайте push до ротации ключей
2. Проверьте что бэкап создан: `ls ../oracul-backup-mirror.git`
3. Обратитесь к `SECURITY_CLEANUP_GUIDE.md` для деталей

---

**Дата:** 12 марта 2026  
**Статус:** ✅ История очищена локально, готово к push после ротации ключей

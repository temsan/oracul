# 🔒 Руководство по очистке секретов из Git истории

## ⚠️ КРИТИЧЕСКИ ВАЖНО

В репозитории обнаружены следующие секреты в файле `archive/old_docs/CLIPROXYAPI_README.md`:

### Скомпрометированные ключи:
- ✅ OpenRouter API Key: `sk-or-v1-[REDACTED]` (удален из текущей версии)
- ✅ GROQ API Key: `gsk_[REDACTED]` (удален из текущей версии)
- ✅ Telegram Bot Token: `[REDACTED]` (удален из текущей версии)
- ✅ Telegram API Hash: `[REDACTED]` (удален из текущей версии)
- ✅ CLIProxyAPI Key: `[REDACTED]` (удален из текущей версии)
- ✅ Gemini API Key: `AIzaSy[REDACTED]` (удален из текущей версии)

### Коммиты с секретами:
- `fe86bcae` - первый коммит с секретами (16 января 2026)
- `091750a` - перемещение в archive (22 января 2026)
- `2a74bcf` - удаление секретов (текущий коммит)

---

## 🚀 Метод 1: Быстрая очистка (рекомендуется)

### Шаг 1: Создайте бэкап

```bash
# Создайте полную копию репозитория
cd ..
git clone oracul oracul-backup-$(date +%Y%m%d)
cd oracul
```

### Шаг 2: Используйте BFG Repo-Cleaner (самый простой способ)

```bash
# Скачайте BFG (Java требуется)
# https://rtyley.github.io/bfg-repo-cleaner/

# Создайте файл со списком секретов
cat > secrets.txt << 'EOF'
oV3wb2nGkZOsp9Li8rKa54d7mtD1MhJU
AIzaSy[REDACTED]
sk-or-v1-[REDACTED]
gsk_[REDACTED]
[REDACTED_BOT_TOKEN]
[REDACTED_API_HASH]
EOF

# Запустите BFG
java -jar bfg.jar --replace-text secrets.txt

# Очистите рефлоги
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## 🔧 Метод 2: Git Filter-Branch (встроенный)

```bash
# Создайте бэкап
git clone . ../oracul-backup

# Замените секреты во всей истории
git filter-branch --force --tree-filter '
if [ -f "archive/old_docs/CLIPROXYAPI_README.md" ]; then
    sed -i.bak "s/oV3wb2nGkZOsp9Li8rKa54d7mtD1MhJU/[REDACTED]/g" "archive/old_docs/CLIPROXYAPI_README.md"
    sed -i.bak "s/AIzaSy[REDACTED]/[REDACTED]/g" "archive/old_docs/CLIPROXYAPI_README.md"
    sed -i.bak "s/sk-or-v1-[REDACTED]/[REDACTED]/g" "archive/old_docs/CLIPROXYAPI_README.md"
    sed -i.bak "s/gsk_[REDACTED]/[REDACTED]/g" "archive/old_docs/CLIPROXYAPI_README.md"
    sed -i.bak "s/[REDACTED_BOT_TOKEN]/[REDACTED]/g" "archive/old_docs/CLIPROXYAPI_README.md"
    sed -i.bak "s/[REDACTED_API_HASH]/[REDACTED]/g" "archive/old_docs/CLIPROXYAPI_README.md"
    rm -f "archive/old_docs/CLIPROXYAPI_README.md.bak"
fi
' --tag-name-filter cat -- --all

# Очистите рефлоги
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## 🔍 Метод 3: Удалить файл из истории полностью

Если файл больше не нужен:

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch archive/old_docs/CLIPROXYAPI_README.md" \
  --prune-empty --tag-name-filter cat -- --all

git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## ✅ Проверка результата

```bash
# Проверьте, что секреты удалены из истории
git log --all --oneline -- archive/old_docs/CLIPROXYAPI_README.md

# Проверьте содержимое старого коммита
git show 091750a:archive/old_docs/CLIPROXYAPI_README.md | grep -i "api.*key"

# Должно показать [REDACTED] вместо реальных ключей
```

---

## 🚀 Отправка изменений

```bash
# ВНИМАНИЕ: Это перезапишет историю на GitHub!
git push origin --force --all
git push origin --force --tags
```

---

## 🔑 ОБЯЗАТЕЛЬНАЯ РОТАЦИЯ КЛЮЧЕЙ

### 1. OpenRouter API Key
- Зайдите на https://openrouter.ai/keys
- Удалите старый ключ
- Создайте новый
- Обновите `.env`

### 2. GROQ API Key
- Зайдите на https://console.groq.com/keys
- Удалите старый ключ
- Создайте новый
- Обновите `.env`

### 3. Telegram Bot Token
- Откройте @BotFather в Telegram
- Отправьте `/revoke`
- Выберите вашего бота
- Получите новый токен
- Обновите `.env`

### 4. Telegram API Credentials
- Зайдите на https://my.telegram.org/apps
- Удалите старое приложение
- Создайте новое
- Обновите `TG_API_ID` и `TG_API_HASH` в `.env`

### 5. Gemini API Key
- Зайдите на https://makersuite.google.com/app/apikey
- Удалите старый ключ
- Создайте новый
- Обновите конфигурацию CLIProxyAPI

---

## 📋 Чеклист

- [ ] Создан бэкап репозитория
- [ ] Выполнена очистка истории (один из методов)
- [ ] Проверено, что секреты удалены из всех коммитов
- [ ] Выполнен force push на GitHub
- [ ] Ротирован OpenRouter API Key
- [ ] Ротирован GROQ API Key
- [ ] Ротирован Telegram Bot Token
- [ ] Ротированы Telegram API credentials
- [ ] Ротирован Gemini API Key
- [ ] Обновлен `.env` файл
- [ ] Проверена работа бота с новыми ключами

---

## ⚠️ Важные замечания

1. После force push все, кто клонировал репозиторий, должны выполнить:
   ```bash
   git fetch origin
   git reset --hard origin/master
   ```

2. Файл `.env` уже в `.gitignore` - проверено ✅

3. Секреты были в публичном репозитории с 16 января 2026

4. GitHub может сохранять кэш старых коммитов до 90 дней

5. Рассмотрите возможность использования GitHub Secrets Scanning:
   https://docs.github.com/en/code-security/secret-scanning

---

## 🆘 Если что-то пошло не так

Восстановите из бэкапа:
```bash
cd ..
rm -rf oracul
mv oracul-backup-YYYYMMDD oracul
cd oracul
```

---

**Дата создания:** 12 марта 2026  
**Статус:** Секреты удалены из текущей версии, требуется очистка истории

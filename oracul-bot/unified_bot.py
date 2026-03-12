#!/usr/bin/env python3
"""
Unified Oracul Bot — точка входа.
Класс UnifiedOracul наследует миксины из bot/ для обработки команд.
"""

import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telethon import TelegramClient, events, Button
from telethon.errors import (
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError
)
from telethon.sessions import StringSession

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.dialog_summary_analyzer_simple import DialogSummaryAnalyzer
from bot.menus import MenuMixin
from bot.chat_handlers import ChatHandlerMixin
from bot.analysis_handlers import AnalysisHandlerMixin
from bot.formatters import FormatterMixin

# Загружаем переменные окружения
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.debug("Загружаем .env из: %s", env_path)
logger.debug("BOT_TOKEN найден: %s", "yes" if os.getenv('BOT_TOKEN') else "no")


class UnifiedOracul(MenuMixin, ChatHandlerMixin, AnalysisHandlerMixin, FormatterMixin):
    """Объединенный бот Oracul с полным функционалом"""

    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.bot_client = None
        self.analyzer = None
        self.api_id = None
        self.api_hash = None
        self.user_clients = {}
        self.pending_auth = {}
        self.auth_storage_path = Path(__file__).parent / "data" / "user_auth_sessions.json"
        self.default_session_ttl_minutes = max(5, int(os.getenv("DEFAULT_SESSION_TTL_MINUTES", "60")))
        self.session_ttl_options = self._parse_ttl_options(
            os.getenv("SESSION_TTL_OPTIONS_MINUTES", "15,60,180,720,1440")
        )
        self.default_session_mode = os.getenv("DEFAULT_SESSION_MODE", "persistent")
        self.session_web_app_url = os.getenv("SESSION_WEB_APP_URL", "").strip()
        self.test_invite_user_id = os.getenv("TEST_INVITE_USER_ID", "").strip()
        self.auth_sessions = self._load_auth_sessions()

        if not self.bot_token:
            logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
            raise ValueError("BOT_TOKEN не настроен")

        logger.info("✅ BOT_TOKEN загружен")

        # Состояния пользователей
        self.user_states = {}

        # Основные категории анализа
        self.analysis_categories = {
            'self_analysis': {
                'name': '💬 Самоанализ диалогов',
                'description': 'Анализ ваших личных диалогов и общения',
                'icon': '💬'
            },
            'psychological': {
                'name': '🧠 Психологический анализ',
                'description': 'Глубокий анализ личности и психотипов',
                'icon': '🧠'
            },
            'voice_analysis': {
                'name': '🎤 Анализ голосовых',
                'description': 'Анализ голосовых сообщений и речи',
                'icon': '🎤'
            },
            'channels_groups': {
                'name': '📊 Каналы и группы',
                'description': 'Анализ активности в каналах и группах',
                'icon': '📊'
            },
            'career_analysis': {
                'name': '💼 Карьерный анализ',
                'description': 'Поиск работы и карьерные рекомендации',
                'icon': '💼'
            },
            'situation_analysis': {
                'name': '🔮 Анализ ситуации',
                'description': 'Комплексный анализ текущего состояния',
                'icon': '🔮'
            }
        }

        # Психологические анализаторы
        self.psychological_analyzers = {
            'big_five': '🧠 Big Five - Модель личности "Большая пятерка"',
            'hero_journey': '⚔️ Путь Героя - 12 этапов развития',
            'psychological_types': '🎭 Психотипы - 4 основных типа личности',
            'jungian_archetypes': '🏛️ Архетипы Юнга - 12 архетипов личности',
            'shadow_work': '🌑 Теневая работа - Скрытые аспекты личности',
            'attachment_styles': '💕 Стили привязанности - Паттерны в отношениях',
            'toxic_relationships': '💔 Токсичные отношения - Юнгианский анализ'
        }

    def _parse_ttl_options(self, options_raw: str) -> list[int]:
        """Парсинг доступных значений TTL сессии (в минутах)."""
        parsed: set[int] = set()
        for item in options_raw.split(","):
            stripped = item.strip()
            if not stripped:
                continue
            try:
                value = int(stripped)
            except ValueError:
                continue
            if value >= 5:
                parsed.add(value)

        parsed.add(self.default_session_ttl_minutes)
        return sorted(parsed)

    def _load_auth_sessions(self) -> dict:
        """Загрузка сохраненных сессий пользователей из JSON."""
        try:
            if not self.auth_storage_path.exists():
                return {}

            with self.auth_storage_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return {}

            return data
        except Exception as error:
            logger.warning(f"Не удалось загрузить хранилище сессий: {error}")
            return {}

    def _save_auth_sessions(self):
        """Сохранение сессий пользователей в JSON."""
        try:
            self.auth_storage_path.parent.mkdir(parents=True, exist_ok=True)
            with self.auth_storage_path.open("w", encoding="utf-8") as file:
                json.dump(self.auth_sessions, file, ensure_ascii=False, indent=2)
        except Exception as error:
            logger.error(f"Не удалось сохранить хранилище сессий: {error}")

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _parse_iso_dt(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            return None

    def _mask_phone(self, phone: str) -> str:
        digits_only = re.sub(r"\D", "", phone)
        if len(digits_only) <= 4:
            return phone
        return f"+{digits_only[:2]}***{digits_only[-2:]}"

    def _ttl_label(self, ttl_minutes: int) -> str:
        if ttl_minutes < 60:
            return f"{ttl_minutes} мин"
        if ttl_minutes % 60 == 0 and ttl_minutes < 1440:
            return f"{ttl_minutes // 60} ч"
        if ttl_minutes % 1440 == 0:
            return f"{ttl_minutes // 1440} д"
        return f"{ttl_minutes} мин"

    def _get_user_record(self, bot_user_id: int) -> dict:
        key = str(bot_user_id)
        record = self.auth_sessions.get(key)
        if not isinstance(record, dict):
            record = {}
            self.auth_sessions[key] = record
        return record

    def _get_user_ttl(self, bot_user_id: int) -> int:
        record = self._get_user_record(bot_user_id)
        ttl = record.get("ttl_minutes", self.default_session_ttl_minutes)
        if not isinstance(ttl, int) or ttl < 5:
            ttl = self.default_session_ttl_minutes
            record["ttl_minutes"] = ttl
            self._save_auth_sessions()
        return ttl

    def _get_user_mode(self, bot_user_id: int) -> str:
        record = self._get_user_record(bot_user_id)
        mode = record.get("session_mode", self.default_session_mode)
        if mode not in {"persistent", "temporary"}:
            mode = self.default_session_mode
            record["session_mode"] = mode
            self._save_auth_sessions()
        return mode

    def _set_user_mode(self, bot_user_id: int, mode: str):
        if mode not in {"persistent", "temporary"}:
            return
        record = self._get_user_record(bot_user_id)
        record["session_mode"] = mode
        record["updated_at"] = self._now().isoformat()
        self._save_auth_sessions()

    def _set_user_ttl(self, bot_user_id: int, ttl_minutes: int):
        record = self._get_user_record(bot_user_id)
        record["ttl_minutes"] = ttl_minutes
        record["updated_at"] = self._now().isoformat()

        expires_at = self._parse_iso_dt(record.get("expires_at"))
        if expires_at and expires_at > self._now():
            record["expires_at"] = (self._now() + timedelta(minutes=ttl_minutes)).isoformat()

        self._save_auth_sessions()

    def _session_is_active(self, record: dict) -> bool:
        session_string = record.get("string_session")
        if not session_string:
            return False
        expires_at = self._parse_iso_dt(record.get("expires_at"))
        return bool(expires_at and expires_at > self._now())

    def _format_expiration(self, expires_at: Optional[str]) -> str:
        expires_dt = self._parse_iso_dt(expires_at)
        if not expires_dt:
            return "не задано"
        local_dt = expires_dt.astimezone()
        return local_dt.strftime("%d.%m.%Y %H:%M")

    async def _cleanup_expired_session(self, bot_user_id: int):
        """Удаление протухшей сессии пользователя и отключение клиента."""
        record = self._get_user_record(bot_user_id)
        if self._session_is_active(record):
            return

        had_session = bool(record.get("string_session"))
        if had_session:
            record.pop("string_session", None)
            record.pop("expires_at", None)
            record["updated_at"] = self._now().isoformat()
            self._save_auth_sessions()

        client = self.user_clients.pop(bot_user_id, None)
        if client:
            try:
                await client.disconnect()
            except Exception:
                pass

    async def get_active_user_client(self, bot_user_id: int) -> Optional[TelegramClient]:
        """Получить авторизованный клиент пользователя с учетом TTL."""
        await self._cleanup_expired_session(bot_user_id)
        record = self._get_user_record(bot_user_id)

        if not self._session_is_active(record):
            return None

        cached_client = self.user_clients.get(bot_user_id)
        if cached_client:
            return cached_client

        session_string = record.get("string_session")
        if not session_string:
            return None

        client = TelegramClient(StringSession(session_string), self.api_id, self.api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()
            record.pop("string_session", None)
            record.pop("expires_at", None)
            self._save_auth_sessions()
            return None

        self.user_clients[bot_user_id] = client
        return client

    async def refresh_user_session_ttl(self, bot_user_id: int):
        """Скользящее продление TTL активной сессии."""
        record = self._get_user_record(bot_user_id)
        if not self._session_is_active(record):
            return
        ttl = self._get_user_ttl(bot_user_id)
        record["expires_at"] = (self._now() + timedelta(minutes=ttl)).isoformat()
        record["updated_at"] = self._now().isoformat()
        self._save_auth_sessions()

    async def require_user_session(self, event, action_name: str) -> Optional[TelegramClient]:
        """Проверка активной пользовательской сессии перед выполнением действий."""
        user_id = event.sender_id
        client = await self.get_active_user_client(user_id)
        if client:
            await self.refresh_user_session_ttl(user_id)
            return client

        text = (
            f"🔐 Для {action_name} нужен вход в вашу личную Telegram-сессию.\n\n"
            f"Нажмите «Войти», поделитесь номером телефона и подтвердите кодом."
        )
        buttons = [
            [Button.inline("🔐 Войти", b"session_login")],
            [Button.inline("⚙️ Сессия", b"session_settings")],
            [Button.inline("◀️ Назад", b"back_to_main")]
        ]
        if hasattr(event, "data"):
            await event.edit(text, buttons=buttons, parse_mode="markdown")
        else:
            await event.respond(text, buttons=buttons, parse_mode="markdown")
        return None

    def _normalize_phone(self, phone_input: str) -> Optional[str]:
        """Нормализация номера телефона пользователя в формате +XXXXXXXXXXX."""
        clean = phone_input.strip()
        if not clean:
            return None
        clean = clean.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if clean.startswith("00"):
            clean = "+" + clean[2:]
        if not clean.startswith("+"):
            clean = "+" + clean

        if not re.fullmatch(r"\+\d{10,15}", clean):
            return None
        return clean

    def _extract_phone_from_message(self, event) -> Optional[str]:
        """Извлечь номер телефона из контакта или текста."""
        message = getattr(event, "message", None)
        if not message:
            return None

        contact = getattr(message, "contact", None)
        if contact and getattr(contact, "phone_number", None):
            return self._normalize_phone(contact.phone_number)

        text = (event.raw_text or "").strip()
        if not text:
            return None
        return self._normalize_phone(text)

    async def show_session_settings(self, event):
        """Экран настроек авторизации и TTL пользовательской сессии."""
        user_id = event.sender_id
        await self._cleanup_expired_session(user_id)
        record = self._get_user_record(user_id)
        ttl = self._get_user_ttl(user_id)
        mode = self._get_user_mode(user_id)
        is_active = self._session_is_active(record)
        phone = record.get("phone")
        expires_at = self._format_expiration(record.get("expires_at"))

        status = "✅ Активна" if is_active else "❌ Неактивна"
        phone_line = self._mask_phone(phone) if phone else "не указан"

        ttl_buttons = []
        for value in self.session_ttl_options[:6]:
            marker = "●" if value == ttl else "○"
            ttl_buttons.append(Button.inline(f"{marker} {self._ttl_label(value)}", f"session_ttl_{value}".encode()))

        rows = [ttl_buttons[i:i + 3] for i in range(0, len(ttl_buttons), 3)]
        mode_buttons = [
            Button.inline(
                f"{'●' if mode == 'persistent' else '○'} TTL",
                b"session_mode_persistent"
            ),
            Button.inline(
                f"{'●' if mode == 'temporary' else '○'} Временный чат",
                b"session_mode_temporary"
            )
        ]
        rows.append(mode_buttons)
        if is_active:
            rows.append([Button.inline("🚪 Выйти из сессии", b"session_logout")])
        else:
            rows.append([Button.inline("🔐 Войти", b"session_login")])
        if self.session_web_app_url:
            rows.append([Button.inline("🧩 Открыть Web App", b"open_webapp")])
        rows.append([Button.inline("◀️ Назад", b"back_to_main")])

        text = (
            "⚙️ **Настройки сессии**\n\n"
            f"Статус: {status}\n"
            f"Телефон: {phone_line}\n"
            f"Режим: {'TTL-сессия' if mode == 'persistent' else 'Временный чат'}\n"
            f"TTL (шкала): {self._ttl_label(ttl)}\n"
            f"Истекает: {expires_at}\n\n"
            "Для отдельной сессии у каждого пользователя выполните личный вход."
        )
        await event.edit(text, buttons=rows, parse_mode="markdown")

    async def start_session_login(self, event):
        """Запрос номера телефона для начала авторизации."""
        user_id = event.sender_id
        self.user_states[user_id] = {"state": "awaiting_phone"}

        # Отправляем сообщение с keyboard кнопкой (нельзя смешивать с inline)
        await event.respond(
            "🔐 **Вход в личную сессию**\n\n"
            "Нажмите кнопку ниже, чтобы поделиться номером телефона, "
            "или отправьте его текстом в формате: +79991234567\n\n"
            "⚠️ **ВАЖНО: Как избежать блокировки входа**\n\n"
            "Код подтверждения придет в Telegram. Если вы введете его здесь "
            "(внутри Telegram), система безопасности **заблокирует вход** - "
            "она подумает что код украли!\n\n"
            "**Что делать когда придет код:**\n"
            "1️⃣ НЕ вводите код в этом чате\n"
            "2️⃣ Откройте Telegram на телефоне\n"
            "3️⃣ Перейдите в Настройки → Устройства\n"
            "4️⃣ Нажмите 'Подтвердить' для нового входа\n\n"
            "Или используйте **тестовый аккаунт** на другой номер (рекомендуется).\n\n"
            "Для отмены отправьте слово 'отмена'.",
            buttons=[
                [Button.request_phone("📱 Поделиться номером")]
            ],
            parse_mode="markdown"
        )

    async def _begin_phone_auth(self, user_id: int, phone: str):
        """Отправить код подтверждения Telegram на номер телефона."""
        if user_id in self.pending_auth:
            pending_client = self.pending_auth[user_id].get("client")
            if pending_client:
                try:
                    await pending_client.disconnect()
                except Exception:
                    pass

        client = TelegramClient(StringSession(), self.api_id, self.api_hash)
        await client.connect()

        code_request = await client.send_code_request(phone)
        self.pending_auth[user_id] = {
            "client": client,
            "phone": phone,
            "phone_code_hash": code_request.phone_code_hash
        }
        self.user_states[user_id] = {"state": "awaiting_login_code"}

    async def _finalize_successful_login(self, user_id: int):
        """Завершение успешного логина: сохранить StringSession и TTL."""
        pending = self.pending_auth.get(user_id)
        if not pending:
            return

        client = pending["client"]
        me = await client.get_me()
        session_string = client.session.save()

        ttl = self._get_user_ttl(user_id)
        expires_at = self._now() + timedelta(minutes=ttl)

        record = self._get_user_record(user_id)
        record["phone"] = pending["phone"]
        record["string_session"] = session_string
        record["telegram_user_id"] = me.id
        record["expires_at"] = expires_at.isoformat()
        record["updated_at"] = self._now().isoformat()
        record["created_at"] = record.get("created_at") or self._now().isoformat()
        self._save_auth_sessions()

        self.user_clients[user_id] = client
        self.pending_auth.pop(user_id, None)
        self.user_states.pop(user_id, None)

    async def _cancel_pending_auth(self, user_id: int):
        pending = self.pending_auth.pop(user_id, None)
        if pending and pending.get("client"):
            try:
                await pending["client"].disconnect()
            except Exception:
                pass

    async def logout_user_session(self, user_id: int):
        """Логаут пользователя из персональной сессии."""
        await self._cancel_pending_auth(user_id)
        self.user_states.pop(user_id, None)

        client = self.user_clients.pop(user_id, None)
        if client:
            try:
                await client.disconnect()
            except Exception:
                pass

        record = self._get_user_record(user_id)
        record.pop("string_session", None)
        record.pop("expires_at", None)
        record["updated_at"] = self._now().isoformat()
        self._save_auth_sessions()

    async def post_request_session_cleanup(self, user_id: int, event):
        """Очистка сессии после запроса для режима временного чата."""
        mode = self._get_user_mode(user_id)
        if mode != "temporary":
            return

        await self.logout_user_session(user_id)
        await event.respond(
            "🧹 Временная сессия завершена и удалена.\n"
            "Для следующего запроса снова выполните вход.",
            buttons=[[Button.inline("🔐 Войти снова", b"session_login")]]
        )

    async def show_web_app_link(self, event):
        """Показать ссылку на Telegram Web App для управления сессией."""
        if not self.session_web_app_url:
            await event.edit(
                "🧩 Web App URL не настроен.\n"
                "Добавьте `SESSION_WEB_APP_URL` в `.env`.",
                buttons=[[Button.inline("◀️ Назад", b"back_to_main")]]
            )
            return

        user_id = event.sender_id
        separator = "&" if "?" in self.session_web_app_url else "?"
        url = f"{self.session_web_app_url}{separator}user_id={user_id}"
        await event.edit(
            "🧩 **Telegram Web App**\n\n"
            "Откройте панель управления сессией:",
            buttons=[
                [Button.url("Открыть Web App", url)],
                [Button.inline("◀️ Назад", b"back_to_main")]
            ],
            parse_mode="markdown"
        )

    async def send_invitation(self, target_user_id: int):
        """Отправить приглашение пользователю в Telegram."""
        invite_text = (
            "🔮 Приглашение в Oracul Bot\n\n"
            "Нажмите /start и авторизуйтесь: у вас будет отдельная сессия с выбором режима:\n"
            "• Persistent (TTL)\n"
            "• Temporary (удаляется после запроса)"
        )
        await self.bot_client.send_message(
            entity=target_user_id,
            message=invite_text,
            buttons=[
                [Button.inline("🚀 Старт", b"back_to_main")],
                [Button.inline("🔐 Сессия", b"session_settings")]
            ]
        )

    async def _handle_auth_message(self, event):
        """Обработка состояний авторизации: телефон, код, 2FA."""
        user_id = event.sender_id
        state = self.user_states.get(user_id, {}).get("state")
        text = (event.raw_text or "").strip()

        if text.lower() in ["отмена", "отмена входа", "cancel"]:
            await self._cancel_pending_auth(user_id)
            self.user_states.pop(user_id, None)
            await event.respond("Вход отменен.", buttons=Button.clear())
            return

        if state == "awaiting_phone":
            phone = self._extract_phone_from_message(event)
            if not phone:
                await event.respond(
                    "Номер не распознан. Отправьте телефон в формате +79991234567 "
                    "или нажмите «Поделиться номером»."
                )
                return

            try:
                await self._begin_phone_auth(user_id, phone)
                await event.respond(
                    "📩 **Код отправлен в Telegram**\n\n"
                    "Введите код цифрами (например: 12345).\n\n"
                    "Если код не пришёл в течение минуты, проверьте:\n"
                    "• Правильность номера телефона\n"
                    "• Соединение с интернетом в Telegram\n"
                    "• Папку 'Спам' в сообщениях",
                    buttons=Button.clear()
                )
            except PhoneNumberInvalidError:
                await event.respond(
                    "❌ **Неверный номер телефона**\n\n"
                    "Проверьте:\n"
                    "• Номер должен начинаться с + (пример: +79991234567)\n"
                    "• Номер должен быть зарегистрирован в Telegram\n"
                    "• Правильно ли выбрана страна",
                    buttons=[[Button.inline("🔐 Попробовать снова", b"session_login")]]
                )
            except Exception as error:
                error_str = str(error).lower()
                logger.error(f"Ошибка отправки кода для {user_id}: {error}")
                
                if "flood" in error_str or "wait" in error_str or "too many" in error_str:
                    await event.respond(
                        "⏳ **Слишком много попыток**\n\n"
                        "Telegram временно ограничил отправку кодов.\n"
                        "Подождите 5-10 минут и попробуйте снова.",
                        buttons=[[Button.inline("🔐 Попробовать снова", b"session_login")]]
                    )
                else:
                    await event.respond(
                        f"❌ **Не удалось отправить код**\n\n"
                        f"Ошибка: {str(error)[:200]}\n\n"
                        "Попробуйте позже или используйте другой номер.",
                        buttons=[[Button.inline("🔐 Попробовать снова", b"session_login")]]
                    )
            return

        if state == "awaiting_login_code":
            pending = self.pending_auth.get(user_id)
            if not pending:
                self.user_states.pop(user_id, None)
                await event.respond("Сессия входа устарела. Запустите вход заново.")
                return

            code = re.sub(r"\D", "", text)
            if len(code) < 3:
                await event.respond("Введите корректный код подтверждения (только цифры).")
                return

            try:
                await pending["client"].sign_in(
                    phone=pending["phone"],
                    code=code,
                    phone_code_hash=pending["phone_code_hash"]
                )
                await self._finalize_successful_login(user_id)
                await event.respond(
                    f"✅ Вход выполнен. Сессия активна до "
                    f"{self._format_expiration(self._get_user_record(user_id).get('expires_at'))}.",
                    buttons=[[Button.inline("⚙️ Открыть сессию", b"session_settings")]]
                )
            except SessionPasswordNeededError:
                self.user_states[user_id] = {"state": "awaiting_2fa_password"}
                await event.respond("Аккаунт защищен 2FA. Отправьте пароль облачного Telegram.")
            except (PhoneCodeInvalidError, PhoneCodeExpiredError):
                await event.respond(
                    "🔒 **Вход заблокирован Telegram**\n\n"
                    "**Почему:** Telegram видит что код подтверждения пришел в ваш аккаунт "
                    "и был введен оттуда же. Система безопасности блокирует такие попытки "
                    "(считает что код мог быть перехвачен).\n\n"
                    "**Решения:**\n\n"
                    "1️⃣ **Подтвердите вход вручную** (самый быстрый способ):\n"
                    "   • Откройте Telegram на телефоне\n"
                    "   • Настройки → Устройства → Подтвердить вход\n\n"
                    "2️⃣ **Подождите 10-15 минут** и попробуйте снова\n\n"
                    "3️⃣ **Используйте другой аккаунт** (рекомендуется для тестов):\n"
                    "   Создайте тестовый аккаунт на другой номер\n\n"
                    "⚠️ **Важно:** Не вводите код из Telegram внутри самого Telegram - "
                    "это вызывает блокировку. Используйте другой способ получения кода "
                    "(SMS на телефон) или подтвердите вход в настройках.",
                    buttons=[[Button.inline("🔐 Попробовать снова", b"session_login")]]
                )
            except Exception as error:
                error_str = str(error).lower()
                logger.error(f"Ошибка подтверждения кода для {user_id}: {error}")
                
                # Проверяем на блокировку входа Telegram'ом
                if "blocked" in error_str or "banned" in error_str or "unauthorized" in error_str:
                    await event.respond(
                        "🔒 **Вход заблокирован Telegram**\n\n"
                        "Telegram обнаружил попытку входа с нового устройства и заблокировал её для защиты.\n\n"
                        "**Что нужно сделать:**\n"
                        "1. Откройте Telegram на телефоне\n"
                        "2. Перейдите в Настройки → Устройства\n"
                        "3. Подтвердите вход с нового устройства\n"
                        "4. Попробуйте войти снова\n\n"
                        "Или подождите 5-10 минут и попробуйте снова.",
                        buttons=[[Button.inline("🔐 Попробовать снова", b"session_login")]]
                    )
                elif "flood" in error_str or "wait" in error_str:
                    await event.respond(
                        "⏳ **Слишком много попыток**\n\n"
                        "Telegram временно ограничил попытки входа.\n"
                        "Подождите 5-10 минут и попробуйте снова.",
                        buttons=[[Button.inline("🔐 Попробовать снова", b"session_login")]]
                    )
                else:
                    await event.respond(
                        "❌ **Не удалось выполнить вход**\n\n"
                        f"Ошибка: {str(error)[:100]}\n\n"
                        "Возможные причины:\n"
                        "• Telegram заблокировал вход с нового устройства\n"
                        "• Включена двухфакторная аутентификация\n"
                        "• Номер телефона некорректен\n\n"
                        "Попробуйте снова или используйте другой аккаунт.",
                        buttons=[[Button.inline("🔐 Попробовать снова", b"session_login")]]
                    )
            return

        if state == "awaiting_2fa_password":
            pending = self.pending_auth.get(user_id)
            if not pending:
                self.user_states.pop(user_id, None)
                await event.respond("Сессия входа устарела. Запустите вход заново.")
                return

            if not text:
                await event.respond("Пароль не может быть пустым. Введите пароль 2FA.")
                return

            try:
                await pending["client"].sign_in(password=text)
                await self._finalize_successful_login(user_id)
                await event.respond(
                    f"✅ Вход выполнен. Сессия активна до "
                    f"{self._format_expiration(self._get_user_record(user_id).get('expires_at'))}.",
                    buttons=[[Button.inline("⚙️ Открыть сессию", b"session_settings")]]
                )
            except Exception as error:
                logger.error(f"Ошибка 2FA для {user_id}: {error}")
                await event.respond("Неверный пароль 2FA. Попробуйте снова.")

    async def _handle_user_text(self, event):
        """Обработка обычного ввода пользователя по состоянию."""
        user_id = event.sender_id
        state = self.user_states.get(user_id, {}).get("state")

        if state in {"awaiting_phone", "awaiting_login_code", "awaiting_2fa_password"}:
            await self._handle_auth_message(event)
            return

        if state == "waiting_chat":
            text = (event.raw_text or "").strip()
            try:
                chat_id = int(text)
            except ValueError:
                await event.respond("Введите числовой ID чата.")
                return
            await self.handle_chat_selection(event, chat_id)
            
        # Психологический анализ - ручной ввод текста
        if state == "waiting_psych_text":
            text = (event.raw_text or "").strip()
            if len(text) < 50:
                await event.respond(
                    "❌ Текст слишком короткий. Минимум 50 символов.",
                    buttons=[[Button.inline('◀️ Назад', b'category_psychological')]]
                )
                return
            
            user_state = self.user_states.get(user_id, {})
            await self.perform_psychological_analysis(
                event, text, 
                user_state.get('analyzer'),
                user_state.get('analyzer_name')
            )
            
        # Психологический анализ - ожидание выбора чата
        if state == "waiting_chat_for_psych":
            text = (event.raw_text or "").strip()
            try:
                chat_id = int(text)
            except ValueError:
                await event.respond("Введите числовой ID чата.")
                return
            
            # Получаем клиент пользователя
            user_client = await self.require_user_session(event, "сбора сообщений")
            if not user_client:
                return
                
            user_state = self.user_states.get(user_id, {})
            
            try:
                await event.respond("🔄 Собираю сообщения из чата...")
                messages = await self.collect_chat_messages(chat_id, user_client=user_client, limit=100)
                
                if not messages:
                    await event.respond(
                        "❌ Не найдено текстовых сообщений в чате.",
                        buttons=[[Button.inline('◀️ Назад', b'category_psychological')]]
                    )
                    return
                
                # Формируем текст из сообщений
                text_parts = []
                for msg in messages[:50]:  # Берем первые 50
                    if msg.get('text'):
                        text_parts.append(msg['text'])
                
                combined_text = "\n".join(text_parts)
                
                if len(combined_text) < 100:
                    await event.respond(
                        "❌ Недостаточно текста для анализа (минимум 100 символов).",
                        buttons=[[Button.inline('◀️ Назад', b'category_psychological')]]
                    )
                    return
                
                await self.perform_psychological_analysis(
                    event, combined_text,
                    user_state.get('analyzer'),
                    user_state.get('analyzer_name')
                )
                
            except Exception as e:
                logger.error(f"Ошибка сбора сообщений: {e}")
                await event.respond(
                    f"❌ Ошибка: {str(e)}",
                    buttons=[[Button.inline('◀️ Назад', b'category_psychological')]]
                )
        
        # Карьерный анализ - ввод профиля
        if state == "waiting_career_profile":
            text = (event.raw_text or "").strip()
            if len(text) < 30:
                await event.respond(
                    "❌ Слишком короткое описание. Минимум 30 символов.",
                    buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]]
                )
                return
            
            await self.perform_career_analysis(event, text, 'career_search')
        
        # Карьерный анализ - резюме
        if state == "waiting_resume":
            text = (event.raw_text or "").strip()
            if len(text) < 50:
                await event.respond(
                    "❌ Резюме слишком короткое. Минимум 50 символов.",
                    buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]]
                )
                return
            
            await self.perform_career_analysis(event, text, 'career_resume')
        
        # Карьерный анализ - зарплата
        if state == "waiting_salary_info":
            text = (event.raw_text or "").strip()
            if len(text) < 20:
                await event.respond(
                    "❌ Информации недостаточно. Опишите позицию и опыт.",
                    buttons=[[Button.inline('◀️ Назад', b'category_career_analysis')]]
                )
                return
            
            await self.perform_career_analysis(event, text, 'career_salary')
        
        # Анализ психологического запроса/проблемы
        if state == "waiting_problem_description":
            text = (event.raw_text or "").strip()
            if len(text) < 50:
                await event.respond(
                    "❌ Описание слишком короткое. Минимум 50 символов.",
                    buttons=[[Button.inline('◀️ Назад', b'category_psychological')]]
                )
                return
            
            await self.perform_problem_analysis(event, text)
    
    async def initialize(self):
        """Инициализация бота"""
        try:
            logger.info("🚀 Инициализация объединенного Oracul бота...")

            api_id = os.getenv('TG_API_ID')
            api_hash = os.getenv('TG_API_HASH')

            if not api_id or api_id == 'YOUR_API_ID_HERE':
                logger.error("❌ TG_API_ID не настроен!")
                return False

            if not api_hash or api_hash == 'YOUR_API_HASH_HERE':
                logger.error("❌ TG_API_HASH не настроен!")
                return False

            try:
                api_id = int(api_id)
            except ValueError:
                logger.error("❌ TG_API_ID должен быть числом!")
                return False

            self.api_id = api_id
            self.api_hash = api_hash
            self.bot_client = TelegramClient('bot_session', api_id, api_hash)
            await self.bot_client.start(bot_token=self.bot_token)
            logger.info("✅ Бот клиент подключен")

            self.analyzer = DialogSummaryAnalyzer()
            await self.analyzer.initialize()

            logger.info("✅ Объединенный Oracul бот готов к работе")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False

    async def handle_start(self, event):
        """Обработка команды /start"""
        user_id = event.sender_id
        await self._cleanup_expired_session(user_id)
        session_active = self._session_is_active(self._get_user_record(user_id))
        session_hint = (
            "✅ Ваша сессия активна"
            if session_active else
            "🔐 Для анализа своих чатов сначала войдите в личную сессию (кнопка «Сессия»)"
        )

        welcome_text = """
🔮 **Добро пожаловать в Unified Oracul Bot!**

Я объединяю в себе все возможности анализа:

**💬 Самоанализ диалогов:**
• Анализ личных чатов и общения
• Голосовые сообщения с CUDA
• Временная динамика

**🧠 Психологический анализ:**
• Big Five, архетипы Юнга
• Путь героя, теневая работа
• Стили привязанности

**🎤 Расширенный анализ голосовых:**
• Эмоциональное состояние
• Динамика отношений
• Паттерны речи

**📊 Анализ каналов и групп:**
• Подписки и интересы
• Влияние контента
• Социальная активность

**💼 Карьерный анализ:**
• Поиск вакансий
• Оптимизация резюме
• Нетворкинг

**🔮 Анализ текущей ситуации:**
• Комплексный анализ
• Рекомендации
• План развития

Выберите категорию анализа:
"""
        welcome_text += f"\n{session_hint}\n"
        await event.respond(
            welcome_text,
            buttons=self.get_main_menu(),
            parse_mode='markdown'
        )

    async def handle_category_selection(self, event, category_id):
        """Обработка выбора категории анализа"""
        category_data = self.analysis_categories.get(category_id)

        if not category_data:
            await event.answer("❌ Категория не найдена")
            return

        menu_map = {
            'self_analysis': self.get_self_analysis_menu,
            'psychological': self.get_psychological_menu,
            'voice_analysis': self.get_voice_analysis_menu,
            'career_analysis': self.get_career_menu,
        }

        if category_id in menu_map:
            prompt = "Выберите тип анализа:" if category_id != 'career_analysis' else "Выберите карьерную функцию:"
            await event.edit(
                f"{category_data['icon']} **{category_data['name']}**\n\n"
                f"{category_data['description']}\n\n{prompt}",
                buttons=menu_map[category_id](),
                parse_mode='markdown'
            )
        elif category_id == 'situation_analysis':
            await event.edit(
                f"{category_data['icon']} **{category_data['name']}**\n\n"
                f"{category_data['description']}\n\n"
                "🔄 Запускаю комплексный анализ вашей текущей ситуации...\n\n"
                "⏳ Это займет 2-3 минуты.",
                parse_mode='markdown'
            )
            await self.perform_situation_analysis(event)
        else:
            await event.edit(
                f"{category_data['icon']} **{category_data['name']}**\n\n"
                f"{category_data['description']}\n\n"
                "🚧 Функция в разработке. Скоро будет доступна!",
                buttons=[[Button.inline('◀️ Назад', b'back_to_main')]],
                parse_mode='markdown'
            )

    async def handle_help(self, event):
        """Обработка помощи"""
        help_text = """
ℹ️ **Unified Oracul Bot - Справка**

**🔮 Возможности:**

**💬 Самоанализ диалогов:**
• Анализ личных чатов
• Голосовые сообщения
• Временная динамика
• Глобальный анализ

**🧠 Психологический анализ:**
• Big Five модель личности
• Архетипы Юнга
• Путь героя (12 этапов)
• Теневая работа
• Стили привязанности

**🎤 Анализ голосовых:**
• Эмоциональное состояние
• Динамика отношений
• Паттерны речи
• Анализ по периодам

**📊 Каналы и группы:**
• Анализ подписок
• Влияние контента
• Социальная активность

**💼 Карьерный анализ:**
• Поиск вакансий
• Оптимизация резюме
• Нетворкинг
• Анализ рынка

**🔮 Анализ ситуации:**
• Комплексный анализ
• Рекомендации
• План развития

**🔒 Конфиденциальность:**
Все данные обрабатываются локально с использованием CUDA и защищенных соединений.

**🔐 Сессия и доступ:**
Для персонального анализа каждый пользователь логинится отдельно по номеру телефона.
Команды: `/login`, `/logout`.
Режимы: TTL или временный чат (авто-удаление сессии после запроса).
Панель: кнопка `Web App`.
"""
        await event.edit(
            help_text,
            buttons=[[Button.inline('◀️ Назад', b'back_to_main')]],
            parse_mode='markdown'
        )

    async def handle_login_command(self, event):
        """Команда /login."""
        await self.start_session_login(event)

    async def handle_logout_command(self, event):
        """Команда /logout."""
        await self.logout_user_session(event.sender_id)
        await event.respond("Вы вышли из личной сессии.", buttons=[[Button.inline("⚙️ Сессия", b"session_settings")]])

    async def run(self):
        """Запуск бота"""
        try:
            if not await self.initialize():
                logger.error("❌ Не удалось инициализировать бота")
                return

            if self.test_invite_user_id:
                try:
                    await self.send_invitation(int(self.test_invite_user_id))
                    logger.info(f"📨 Приглашение отправлено пользователю {self.test_invite_user_id}")
                except Exception as error:
                    logger.warning(f"Не удалось отправить приглашение {self.test_invite_user_id}: {error}")

            @self.bot_client.on(events.NewMessage(pattern='/start'))
            async def start_handler(event):
                await self.handle_start(event)

            @self.bot_client.on(events.NewMessage(pattern='/help'))
            async def help_handler(event):
                await self.handle_help(event)

            @self.bot_client.on(events.NewMessage(pattern='/login'))
            async def login_handler(event):
                await self.handle_login_command(event)

            @self.bot_client.on(events.NewMessage(pattern='/logout'))
            async def logout_handler(event):
                await self.handle_logout_command(event)

            @self.bot_client.on(events.NewMessage)
            async def user_text_handler(event):
                if event.raw_text and event.raw_text.startswith('/'):
                    return
                await self._handle_user_text(event)

            @self.bot_client.on(events.CallbackQuery)
            async def callback_handler(event):
                await self._route_callback(event)

            logger.info("🤖 Unified Oracul бот запущен и готов к работе!")
            logger.info("📱 Отправьте /start боту для начала работы")

            await self.bot_client.run_until_disconnected()

        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал остановки")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.bot_client:
                await self.bot_client.disconnect()
            for pending in self.pending_auth.values():
                pending_client = pending.get("client")
                if pending_client:
                    try:
                        await pending_client.disconnect()
                    except Exception:
                        pass
            for client in self.user_clients.values():
                try:
                    await client.disconnect()
                except Exception:
                    pass
            logger.info("👋 Бот остановлен")

    async def _route_callback(self, event):
        """Маршрутизация callback-запросов от кнопок"""
        data = event.data.decode()

        # Навигация по категориям
        if data.startswith('category_'):
            category_id = data.split('_', 1)[1]
            await self.handle_category_selection(event, category_id)
        elif data == 'back_to_main':
            await event.edit(
                "🔮 **Главное меню**\n\nВыберите категорию анализа:",
                buttons=self.get_main_menu(),
                parse_mode='markdown'
            )
        elif data == 'help':
            await self.handle_help(event)
        elif data in ('settings', 'session_settings'):
            await self.show_session_settings(event)
        elif data == 'session_login':
            await self.start_session_login(event)
        elif data == 'session_logout':
            await self.logout_user_session(event.sender_id)
            await self.show_session_settings(event)
        elif data == 'session_mode_persistent':
            self._set_user_mode(event.sender_id, "persistent")
            await self.show_session_settings(event)
        elif data == 'session_mode_temporary':
            self._set_user_mode(event.sender_id, "temporary")
            await self.show_session_settings(event)
        elif data.startswith('session_ttl_'):
            try:
                ttl_value = int(data.split('_')[-1])
            except ValueError:
                await event.answer("Некорректное значение TTL")
                return
            if ttl_value not in self.session_ttl_options:
                await event.answer("Недоступное значение TTL")
                return
            self._set_user_ttl(event.sender_id, ttl_value)
            await self.show_session_settings(event)
        elif data == 'open_webapp':
            await self.show_web_app_link(event)

        # Чаты
        elif data in ('select_chat', 'show_chats'):
            await self.handle_show_chats(event)
        elif data == 'show_groups_channels':
            await self.handle_show_groups_channels(event)
        elif data == 'show_all_personal':
            await self.handle_show_all_personal(event)
        elif data == 'show_all_groups':
            await self.handle_show_all_groups(event)
        elif data == 'show_all_channels':
            await self.handle_show_all_channels(event)
        elif data.startswith('chat_'):
            chat_id = int(data.split('_', 1)[1])
            await self.handle_chat_selection(event, chat_id)

        # Типы анализа
        elif data == 'quick_analysis':
            await self.handle_quick_analysis(event)
        elif data == 'deep_analysis':
            await self.handle_deep_analysis(event)
        elif data == 'voice_only':
            await self.handle_voice_only(event)
        elif data == 'text_only':
            await self.handle_text_only(event)
        elif data == 'last_week':
            await self.handle_time_period(event, 'last_week')
        elif data == 'last_month':
            await self.handle_time_period(event, 'last_month')
        elif data == 'global_analysis':
            await self.handle_global_analysis(event)
        elif data.startswith('global_'):
            await self.handle_global_period(event, data)

        # Психологический анализ
        elif data.startswith('psych_'):
            analyzer_type = data.split('_', 1)[1]
            await self.handle_psychological_analysis(event, analyzer_type)
        elif data == 'advanced_psych':
            await self.handle_advanced_psychological_menu(event)
        elif data == 'manual_psych_input':
            await self.handle_manual_psych_input(event)
        elif data == 'auto_psych_collect':
            await self.handle_auto_psych_collect(event)
        elif data == 'psych_problem_analysis':
            await self.handle_problem_analysis(event)
        elif data == 'book_consultation':
            await self.handle_book_consultation(event)

        # Голосовой анализ
        elif data == 'voice_periods':
            await self.handle_voice_periods(event)
        elif data == 'voice_focus':
            await self.handle_voice_focus(event)
        elif data == 'voice_users':
            await self.handle_voice_users(event)
        elif data == 'voice_emotions':
            await self.handle_voice_emotions(event)
        elif data == 'voice_relationships':
            await self.handle_voice_relationships(event)
        elif data == 'voice_patterns':
            await self.handle_voice_patterns(event)

        # Карьерный анализ - реализация
        elif data == 'career_enter_profile':
            await self.handle_career_search(event)
        elif data == 'career_analyze_network':
            await self._perform_network_analysis(event)
        elif data == 'career_market_it':
            await self._perform_market_analysis(event, 'IT')
        elif data == 'career_market_business':
            await self._perform_market_analysis(event, 'Business')
        elif data == 'career_market_design':
            await self._perform_market_analysis(event, 'Design')

        # Карьерный анализ
        elif data == 'career_search':
            await self.handle_career_search(event)
        elif data == 'career_resume':
            await self.handle_career_resume(event)
        elif data == 'career_networking':
            await self.handle_career_networking(event)
        elif data == 'career_market':
            await self.handle_career_market(event)
        elif data == 'career_salary':
            await self.handle_career_salary(event)

        # Общие
        elif data == 'history':
            await self.handle_history(event)
        else:
            await event.answer("⚠️ Функция в разработке")


async def main():
    """Главная функция"""
    bot = UnifiedOracul()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())

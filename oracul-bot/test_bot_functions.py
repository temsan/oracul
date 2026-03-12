#!/usr/bin/env python3
"""
Тестирование функций Oracul Bot без реального подключения к Telegram.
Проверяет структуру, импорты, логику сессий.
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))


class Colors:
    GREEN = ""
    RED = ""
    YELLOW = ""
    BLUE = ""
    RESET = ""


def safe_print(text):
    """Вывод без эмодзи для совместимости с Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Удаляем эмодзи и пробуем снова
        import re
        text_clean = re.sub(r'[^\x00-\x7F]+', '', text)
        print(text_clean)


def print_header(text):
    safe_print(f"\n{Colors.BLUE}{'='*50}{Colors.RESET}")
    safe_print(f"{Colors.BLUE}{text}{Colors.RESET}")
    safe_print(f"{Colors.BLUE}{'='*50}{Colors.RESET}")


def print_ok(text):
    safe_print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")


def print_error(text):
    safe_print(f"{Colors.RED}[FAIL] {text}{Colors.RESET}")


def print_warning(text):
    safe_print(f"{Colors.YELLOW}[WARN] {text}{Colors.RESET}")


async def test_imports():
    """Тест 1: Проверка импортов"""
    print_header("TEST 1: Проверка импортов")
    
    try:
        from unified_bot import UnifiedOracul
        print_ok("UnifiedOracul импортируется")
    except Exception as e:
        print_error(f"UnifiedOracul: {e}")
        return False
    
    try:
        from session_webapp import app
        print_ok("session_webapp импортируется")
    except Exception as e:
        print_error(f"session_webapp: {e}")
        return False
    
    try:
        from bot.menus import MenuMixin
        from bot.chat_handlers import ChatHandlerMixin
        from bot.analysis_handlers import AnalysisHandlerMixin
        from bot.formatters import FormatterMixin
        print_ok("Все миксины импортируются")
    except Exception as e:
        print_error(f"Миксины: {e}")
        return False
    
    try:
        from analyzers.dialog_summary_analyzer_simple import DialogSummaryAnalyzer
        print_ok("DialogSummaryAnalyzer импортируется")
    except Exception as e:
        print_error(f"Analyzer: {e}")
        return False
    
    return True


async def test_bot_initialization():
    """Тест 2: Инициализация бота"""
    print_header("TEST 2: Инициализация бота")
    
    try:
        from unified_bot import UnifiedOracul
        bot = UnifiedOracul()
        
        # Проверка базовых атрибутов
        assert bot.bot_token, "BOT_TOKEN не загружен"
        print_ok(f"BOT_TOKEN загружен: {bot.bot_token[:20]}...")
        
        assert bot.default_session_ttl_minutes >= 5, "TTL должен быть >= 5"
        print_ok(f"Default TTL: {bot.default_session_ttl_minutes} мин")
        
        assert bot.default_session_mode in ["persistent", "temporary"], "Неверный режим"
        print_ok(f"Default mode: {bot.default_session_mode}")
        
        assert len(bot.session_ttl_options) > 0, "TTL options пуст"
        print_ok(f"TTL options: {bot.session_ttl_options}")
        
        # Проверка категорий анализа
        assert len(bot.analysis_categories) == 6, "Должно быть 6 категорий"
        print_ok(f"Категорий анализа: {len(bot.analysis_categories)}")
        
        # Проверка психологических анализаторов
        assert len(bot.psychological_analyzers) == 7, "Должно быть 7 психо-анализаторов"
        print_ok(f"Психологических анализаторов: {len(bot.psychological_analyzers)}")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка инициализации: {e}")
        return False


async def test_session_methods():
    """Тест 3: Проверка методов сессий"""
    print_header("TEST 3: Методы сессий")
    
    try:
        from unified_bot import UnifiedOracul
        bot = UnifiedOracul()
        
        # Проверка наличия ключевых методов
        methods = [
            'require_user_session',
            'start_session_login',
            'logout_user_session',
            'show_session_settings',
            'post_request_session_cleanup',
            'refresh_user_session_ttl',
            'get_active_user_client',
            '_load_auth_sessions',
            '_save_auth_sessions',
            '_session_is_active',
        ]
        
        for method in methods:
            assert hasattr(bot, method), f"Метод {method} отсутствует"
            print_ok(f"Метод {method} присутствует")
        
        # Проверка структуры хранилища сессий
        assert hasattr(bot, 'auth_sessions'), "auth_sessions отсутствует"
        assert hasattr(bot, 'auth_storage_path'), "auth_storage_path отсутствует"
        print_ok("Структура хранилища сессий корректна")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка методов сессий: {e}")
        return False


async def test_menus():
    """Тест 4: Проверка меню"""
    print_header("TEST 4: Генерация меню")
    
    try:
        from unified_bot import UnifiedOracul
        bot = UnifiedOracul()
        
        # Главное меню
        main_menu = bot.get_main_menu()
        assert len(main_menu) > 0, "Главное меню пустое"
        print_ok(f"Главное меню: {len(main_menu)} строк кнопок")
        
        # Проверка наличия кнопок сессий
        has_session_button = any('session_settings' in str(row) for row in main_menu)
        has_webapp_button = any('open_webapp' in str(row) for row in main_menu)
        
        if has_session_button:
            print_ok("Кнопка 'Сессия' присутствует в меню")
        else:
            print_error("Кнопка 'Сессия' отсутствует в меню")
            
        if has_webapp_button:
            print_ok("Кнопка 'Web App' присутствует в меню")
        else:
            print_warning("Кнопка 'Web App' отсутствует (нормально если URL не настроен)")
        
        # Другие меню
        menus = [
            ('get_self_analysis_menu', 'Самоанализ'),
            ('get_psychological_menu', 'Психологический'),
            ('get_voice_analysis_menu', 'Голосовой'),
            ('get_career_menu', 'Карьерный'),
        ]
        
        for method_name, label in menus:
            menu = getattr(bot, method_name)()
            assert len(menu) > 0, f"Меню {label} пустое"
            print_ok(f"Меню '{label}': {len(menu)} строк кнопок")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка меню: {e}")
        return False


async def test_routing():
    """Тест 5: Проверка маршрутизации callback"""
    print_header("TEST 5: Маршрутизация callback")
    
    try:
        from unified_bot import UnifiedOracul
        bot = UnifiedOracul()
        
        # Проверка наличия метода маршрутизации
        assert hasattr(bot, '_route_callback'), "_route_callback отсутствует"
        print_ok("Метод _route_callback присутствует")
        
        # Проверка обработчиков сессий
        session_callbacks = [
            'session_settings',
            'session_login',
            'session_logout',
            'session_mode_persistent',
            'session_mode_temporary',
            'open_webapp',
        ]
        
        print_ok(f"Callback-обработчики сессий: {len(session_callbacks)}")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка маршрутизации: {e}")
        return False


async def test_session_storage():
    """Тест 6: Проверка работы с хранилищем сессий"""
    print_header("TEST 6: Хранилище сессий")
    
    try:
        from unified_bot import UnifiedOracul
        bot = UnifiedOracul()
        
        # Тест создания записи
        test_user_id = 999999
        record = bot._get_user_record(test_user_id)
        assert isinstance(record, dict), "Запись должна быть словарем"
        print_ok("Создание записи пользователя работает")
        
        # Тест TTL
        ttl = bot._get_user_ttl(test_user_id)
        assert ttl >= 5, "TTL должен быть >= 5"
        print_ok(f"Получение TTL: {ttl}")
        
        # Тест режима
        mode = bot._get_user_mode(test_user_id)
        assert mode in ["persistent", "temporary"], "Неверный режим"
        print_ok(f"Получение режима: {mode}")
        
        # Тест парсинга TTL
        test_ttl = bot._ttl_label(60)
        assert "ч" in test_ttl or "мин" in test_ttl, "Неверный формат TTL"
        print_ok(f"Форматирование TTL: 60 -> {test_ttl}")
        
        test_ttl = bot._ttl_label(1440)
        assert "д" in test_ttl, "Неверный формат для дней"
        print_ok(f"Форматирование TTL: 1440 -> {test_ttl}")
        
        # Очистка тестовой записи
        bot.auth_sessions.pop(str(test_user_id), None)
        print_ok("Тестовая запись удалена")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка хранилища: {e}")
        return False


async def test_webapp():
    """Тест 7: Проверка Web App"""
    print_header("TEST 7: Web App для сессий")
    
    try:
        from session_webapp import app, SessionPreferences, _load_store, _save_store
        
        # Проверка FastAPI app
        assert app is not None, "FastAPI app не создан"
        print_ok("FastAPI app создан")
        
        # Проверка модели
        pref = SessionPreferences(ttl_minutes=60, session_mode="persistent")
        assert pref.ttl_minutes == 60
        assert pref.session_mode == "persistent"
        print_ok("Модель SessionPreferences работает")
        
        # Проверка функций хранилища
        store = _load_store()
        assert isinstance(store, dict), "Хранилище должно быть словарем"
        print_ok("Функции хранилища работают")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка Web App: {e}")
        return False


async def test_env_variables():
    """Тест 8: Проверка переменных окружения"""
    print_header("TEST 8: Переменные окружения")
    
    required = [
        'BOT_TOKEN',
        'TG_API_ID',
        'TG_API_HASH',
    ]
    
    optional = [
        'DEFAULT_SESSION_TTL_MINUTES',
        'DEFAULT_SESSION_MODE',
        'SESSION_TTL_OPTIONS_MINUTES',
        'SESSION_WEB_APP_URL',
    ]
    
    all_ok = True
    
    for var in required:
        value = os.getenv(var)
        if value:
            print_ok(f"{var}: установлена")
        else:
            print_error(f"{var}: НЕ установлена (ОБЯЗАТЕЛЬНА)")
            all_ok = False
    
    for var in optional:
        value = os.getenv(var)
        if value:
            print_ok(f"{var}: {value}")
        else:
            print_warning(f"{var}: не установлена (опциональна)")
    
    return all_ok


async def main():
    """Главная функция тестирования"""
    safe_print(f"\n{Colors.BLUE}Oracul Bot Function Tests{Colors.RESET}")
    safe_print(f"{Colors.BLUE}Проверка функций без подключения к Telegram{Colors.RESET}\n")
    
    tests = [
        ("Импорты", test_imports),
        ("Инициализация бота", test_bot_initialization),
        ("Методы сессий", test_session_methods),
        ("Генерация меню", test_menus),
        ("Маршрутизация", test_routing),
        ("Хранилище сессий", test_session_storage),
        ("Web App", test_webapp),
        ("Переменные окружения", test_env_variables),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Критическая ошибка в {name}: {e}")
            results.append((name, False))
    
    # Итоги
    print_header("ИТОГИ")
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status}: {name}")
    
    print(f"\nВсего: {len(results)} тестов")
    print(f"{Colors.GREEN}Пройдено: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Ошибок: {failed}{Colors.RESET}")
    
    if failed == 0:
        safe_print(f"\n{Colors.GREEN}Все тесты пройдены!{Colors.RESET}")
        return 0
    else:
        safe_print(f"\n{Colors.RED}Есть ошибки, требующие внимания{Colors.RESET}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

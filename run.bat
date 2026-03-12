@echo off
chcp 65001 >nul
title Oracul Bot Launcher

echo ==========================================
echo    Oracul Bot - Unified Launcherecho ==========================================
echo.

if "%~1"=="" (
    echo 🚀 Запуск только бота...
    python run.py
) else if "%~1"=="--webapp" (
    echo 🚀 Запуск бота + Web App...
    python run.py --webapp
) else if "%~1"=="--webapp-only" (
    echo 🌐 Запуск только Web App...
    python run.py --webapp-only
) else (
    echo Использование:
    echo   run.bat              - Запуск только бота
    echo   run.bat --webapp     - Запуск бота + Web App
    echo   run.bat --webapp-only - Запуск только Web App
)

pause

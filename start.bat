@echo off
echo 🤖 Запуск бота NoolShy Fame
echo =============================

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Установите Python с python.org
    pause
    exit /b 1
)

REM Устанавливаем зависимости
echo 📦 Установка зависимостей...
pip install requests

REM Запускаем бота
echo 🤖 Запуск бота...
python bot.py

pause
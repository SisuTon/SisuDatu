#!/bin/bash

set -e

PYTHON_VERSION=3.11

# Проверка Python
if ! command -v python$PYTHON_VERSION &> /dev/null; then
    echo "❌ Python $PYTHON_VERSION не найден. Установите его и повторите попытку."
    exit 1
else
    echo "🔍 Проверка Python $PYTHON_VERSION..."
    echo "✅ Python $PYTHON_VERSION найден."
fi

# Активация виртуального окружения
if [ -d ".venv" ]; then
    echo "⚙️ Активация виртуального окружения..."
    source .venv/bin/activate
else
    echo "❌ Виртуальное окружение не найдено. Создайте его с помощью 'python$PYTHON_VERSION -m venv .venv'"
    exit 1
fi

# Установка зависимостей
if [ -f "requirements.txt" ]; then
    echo "📦 Установка зависимостей..."
    pip install -r requirements.txt
fi

# Запуск бота
export PYTHONPATH=.
echo "🚀 Запуск бота..."
python -m app.main 
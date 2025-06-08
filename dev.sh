#!/bin/bash

PYTHON_VERSION="3.11"
VENV_DIR=".venv"

echo "🔍 Проверка Python $PYTHON_VERSION..."

if ! command -v python$PYTHON_VERSION &> /dev/null
then
    echo "❌ Python $PYTHON_VERSION не найден. Установи через brew: brew install python@$PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION найден."

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Создание виртуального окружения..."
    python$PYTHON_VERSION -m venv $VENV_DIR
fi

echo "⚙️ Активация виртуального окружения..."
source $VENV_DIR/bin/activate

echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Запуск бота..."
export PYTHONPATH=sisu_bot
python -m sisu_bot.main 
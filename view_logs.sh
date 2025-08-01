#!/bin/bash

# Скрипт для просмотра логов и состояния проекта

echo "🔍 АНАЛИЗ ПРОЕКТА SISUDATUBOT"
echo "================================"

# Git статус
echo -e "\n📋 GIT СТАТУС:"
git status --short

echo -e "\n📋 ПОСЛЕДНИЕ КОММИТЫ:"
git log --oneline -5

# Логи
echo -e "\n📋 ЛОГИ:"
if [ -d "logs" ]; then
    echo "Найденные файлы логов:"
    ls -la logs/*.log 2>/dev/null || echo "Файлы логов не найдены"
    
    echo -e "\n📋 ПОСЛЕДНИЕ ОШИБКИ (последние 10 строк):"
    for log in logs/*.log; do
        if [ -f "$log" ]; then
            echo "=== $log ==="
            grep -i "error\|exception\|traceback" "$log" | tail -10
        fi
    done
else
    echo "Папка logs не найдена"
fi

# Структура проекта
echo -e "\n📁 СТРУКТУРА ПРОЕКТА:"
echo "Основные директории:"
ls -la | grep "^d"

echo -e "\n📁 SISU_BOT СТРУКТУРА:"
if [ -d "sisu_bot" ]; then
    find sisu_bot -type d -maxdepth 2 | head -20
else
    echo "Папка sisu_bot не найдена"
fi

# Python файлы
echo -e "\n🐍 PYTHON ФАЙЛЫ (первые 20):"
find . -name "*.py" -not -path "./venv/*" -not -path "./__pycache__/*" | head -20

# Конфигурационные файлы
echo -e "\n⚙️ КОНФИГУРАЦИОННЫЕ ФАЙЛЫ:"
ls -la *.txt *.toml *.yml *.yaml *.json 2>/dev/null || echo "Конфигурационные файлы не найдены"

# Запущенные процессы
echo -e "\n🔄 ЗАПУЩЕННЫЕ ПРОЦЕССЫ:"
ps aux | grep -i "python\|sisu" | grep -v grep || echo "Процессы не найдены"

# Использование диска
echo -e "\n💾 ИСПОЛЬЗОВАНИЕ ДИСКА:"
du -sh . 2>/dev/null || echo "Не удалось получить информацию о диске"

echo -e "\n✅ АНАЛИЗ ЗАВЕРШЕН" 
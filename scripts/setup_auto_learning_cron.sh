#!/bin/bash
# Скрипт для настройки автоматического автообучения через cron

echo "🤖 Настройка автоматического автообучения SisuDatuBot"
echo "=================================================="

# Получаем абсолютный путь к проекту
PROJECT_DIR="/Users/byorg/Desktop/SisuDatuBot"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/scripts/run_auto_learning.py"

echo "📁 Проект: $PROJECT_DIR"
echo "🐍 Python: $PYTHON_PATH"
echo "📜 Скрипт: $SCRIPT_PATH"

# Проверяем существование файлов
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python не найден по пути: $PYTHON_PATH"
    echo "   Убедитесь, что виртуальное окружение создано"
    exit 1
fi

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Скрипт автообучения не найден: $SCRIPT_PATH"
    exit 1
fi

# Делаем скрипт исполняемым
chmod +x "$SCRIPT_PATH"

echo "✅ Файлы проверены"

# Создаем cron job для запуска каждые 6 часов
CRON_JOB="0 */6 * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $PROJECT_DIR/auto_learning.log 2>&1"

echo ""
echo "📅 Предлагаемый cron job (каждые 6 часов):"
echo "$CRON_JOB"
echo ""

# Спрашиваем пользователя
read -p "Добавить этот cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Добавляем cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron job добавлен успешно!"
        echo ""
        echo "📋 Текущие cron jobs:"
        crontab -l | grep -E "(auto_learning|SisuDatuBot)" || echo "   (не найдены)"
    else
        echo "❌ Ошибка добавления cron job"
        exit 1
    fi
else
    echo "ℹ️  Cron job не добавлен"
    echo "   Вы можете добавить его вручную командой:"
    echo "   crontab -e"
    echo "   И вставить строку:"
    echo "   $CRON_JOB"
fi

echo ""
echo "🎉 Настройка завершена!"
echo ""
echo "📝 Дополнительная информация:"
echo "   • Логи автообучения: $PROJECT_DIR/auto_learning.log"
echo "   • Ручной запуск: $PYTHON_PATH $SCRIPT_PATH"
echo "   • Просмотр cron jobs: crontab -l"
echo "   • Удаление cron job: crontab -e (удалить строку)"

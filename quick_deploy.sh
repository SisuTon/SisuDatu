#!/bin/bash
# Скрипт для быстрого тестирования и деплоя бота Sisu
# Автор: AI Assistant

set -e  # Остановка при ошибке

echo "🚀 Запуск быстрого тестирования и деплоя бота Sisu..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверяем наличие виртуального окружения
if [ ! -d ".venv" ]; then
    log_error "Виртуальное окружение не найдено!"
    log_info "Создаем виртуальное окружение..."
    python3 -m venv .venv
fi

# Активируем виртуальное окружение
log_info "Активируем виртуальное окружение..."
source .venv/bin/activate

# Проверяем Python версию
PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
log_info "Версия Python: $PYTHON_VERSION"

# Устанавливаем зависимости
log_info "Устанавливаем зависимости..."
pip install -r requirements.txt

# Проверяем конфигурацию
log_info "Проверяем конфигурацию..."
python check_config.py

if [ $? -ne 0 ]; then
    log_error "Проблемы с конфигурацией!"
    log_info "Создаем шаблон .env файла..."
    python check_config.py --create-template
    log_warning "Заполните .env файл и запустите скрипт снова!"
    exit 1
fi

# Запускаем тесты функционала
log_info "Запускаем тесты функционала..."
python test_bot_functionality.py

if [ $? -ne 0 ]; then
    log_error "Тесты не прошли!"
    exit 1
fi

# Проверяем синтаксис Python файлов
log_info "Проверяем синтаксис Python файлов..."
python -m py_compile sisu_bot/main.py
python -m py_compile sisu_bot/bot/bot.py

# Проверяем импорты
log_info "Проверяем импорты..."
python -c "
import sys
sys.path.append('.')
try:
    from sisu_bot.bot.bot import bot
    from sisu_bot.bot.handlers import *
    print('✅ Все импорты успешны')
except Exception as e:
    print(f'❌ Ошибка импорта: {e}')
    sys.exit(1)
"

# Останавливаем предыдущие процессы бота
log_info "Останавливаем предыдущие процессы бота..."
pkill -f "python.*sisu_bot/main.py" || true
pkill -f "python.*main.py" || true

# Ждем завершения процессов
sleep 2

# Запускаем бота в фоне
log_info "Запускаем бота..."
nohup python sisu_bot/main.py > bot.log 2>&1 &
BOT_PID=$!

# Ждем запуска
sleep 5

# Проверяем, что бот запустился
if ps -p $BOT_PID > /dev/null; then
    log_success "Бот успешно запущен! PID: $BOT_PID"
    log_info "Логи бота: tail -f bot.log"
    log_info "Остановить бота: kill $BOT_PID"
    
    # Показываем последние логи
    log_info "Последние логи бота:"
    tail -n 20 bot.log
    
else
    log_error "Не удалось запустить бота!"
    log_info "Проверьте логи: cat bot.log"
    exit 1
fi

# Показываем статус
log_success "🎉 Деплой завершен успешно!"
log_info "Бот работает в фоновом режиме"
log_info "Для мониторинга используйте: tail -f bot.log"
log_info "Для остановки: kill $BOT_PID"

# Создаем скрипт для остановки
cat > stop_bot.sh << EOF
#!/bin/bash
echo "🛑 Останавливаем бота..."
kill $BOT_PID 2>/dev/null || true
pkill -f "python.*sisu_bot/main.py" 2>/dev/null || true
echo "✅ Бот остановлен"
EOF

chmod +x stop_bot.sh
log_info "Создан скрипт остановки: ./stop_bot.sh"

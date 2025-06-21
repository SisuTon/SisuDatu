#!/bin/bash
set -e
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
echo "📦 Бэкап базы данных..."
cp sisu_bot.db $BACKUP_DIR/
echo "📦 Бэкап json-файлов..."
cp data/*.json $BACKUP_DIR/ 2>/dev/null || echo "Нет json-файлов для бэкапа."
echo "✅ Бэкап сохранён в $BACKUP_DIR" 
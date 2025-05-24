FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей и создание директорий в одном слое
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p data/cache logs

# Копирование кода
COPY . .

# Запуск бота
CMD ["python", "main.py"] 
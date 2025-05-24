FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей и создание директорий в одном слое
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p logs

# Копирование кода
COPY . .

# Запуск админ-панели
CMD ["uvicorn", "admin_panel.main:app", "--host", "0.0.0.0", "--port", "8000"] 
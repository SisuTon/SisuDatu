# SisuDatuBot - Modern DI Architecture (2025)

## 🏗️ Архитектура

### Структура проекта:
```
app/
├── core/                    # DI контейнер и ядро
│   ├── container.py        # Основной контейнер
│   ├── lifespan.py         # Управление жизненным циклом
│   └── exceptions.py       # Кастомные исключения
├── domain/                 # Бизнес-логика
│   ├── entities/           # Сущности
│   ├── repositories/       # Интерфейсы БД
│   ├── services/           # Use Cases
│   └── events/             # Доменные события
├── infrastructure/         # Внешние системы
│   ├── db/                # База данных
│   ├── ai/                # AI сервисы
│   ├── cache/             # Кэширование
│   └── storage/           # Файловое хранилище
└── presentation/           # Пользовательский интерфейс
    ├── api/               # REST API
    └── bot/               # Telegram handlers
```

## 🚀 Быстрый старт

### 1. Установка зависимостей:
```bash
pip install -r requirements.txt
```

### 2. Настройка окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл
```

### 3. Запуск:
```bash
python app/main.py
```

## 🧪 Тестирование

### Unit тесты:
```bash
pytest tests/unit/
```

### Integration тесты:
```bash
pytest tests/integration/
```

### Coverage:
```bash
pytest --cov=app tests/
```

## 📦 DI Преимущества

- ✅ **Чистая архитектура** - разделение на слои
- ✅ **Легкое тестирование** - подмена зависимостей
- ✅ **Замена реализаций** - без изменения кода
- ✅ **Модульность** - независимые компоненты
- ✅ **Масштабируемость** - легко добавлять новые фичи

## 🔧 Разработка

### Добавление нового сервиса:
1. Создайте интерфейс в `domain/repositories/`
2. Реализуйте в `infrastructure/db/repositories/`
3. Добавьте в контейнер `core/container.py`
4. Используйте в сервисах через `@inject`

### Пример:
```python
@inject
def handler(
    user_service: UserService = Provide[Container.user_service]
):
    return user_service.get_user(123)
```
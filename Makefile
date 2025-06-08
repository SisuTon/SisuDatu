.PHONY: install test deploy backup clean clean-pyc clean-test clean-build dev docker run lint

# Установка (кросс-платформенная)
install:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt || venv/Scripts/pip install -r requirements.txt
	@echo "✅ Виртуальное окружение создано и зависимости установлены"
	@echo "📝 Не забудь активировать venv:"
	@echo "   source venv/bin/activate  # для Linux/Mac"
	@echo "   venv/Scripts/activate     # для Windows"

# Тесты
test:
	pytest tests/

# Деплой
deploy:
	docker-compose up -d --build

# Бэкап (с проверкой)
backup:
	@if [ -x ./scripts/backup.sh ]; then \
		./scripts/backup.sh; \
	else \
		echo "❌ backup.sh не найден или не исполняемый"; \
		exit 1; \
	fi

# Очистка Python кэша
clean-pyc:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +
	@echo "✅ Python кэш очищен"

# Очистка тестов
clean-test:
	rm -rf .pytest_cache .coverage htmlcov
	@echo "✅ Тестовые файлы очищены"

# Очистка сборки
clean-build:
	rm -rf build dist *.egg-info
	@echo "✅ Файлы сборки очищены"

# Полная очистка
clean: clean-pyc clean-test clean-build
	@echo "✅ Все временные файлы очищены"

dev:
	./dev.sh

docker:
	docker build -t sisu-bot .

run:
	docker run --env-file .env sisu-bot

lint:
	black . && flake8 . 
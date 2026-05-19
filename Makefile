.PHONY: help up down build test lint format migrate shell

help:
	@echo "Доступные команды:"
	@echo "  make up        - Запустить все контейнеры"
	@echo "  make down      - Остановить все контейнеры"
	@echo "  make build     - Пересобрать образы"
	@echo "  make test      - Запустить тесты"
	@echo "  make lint      - Проверить ruff"
	@echo "  make format    - Отформатировать ruff"
	@echo "  make migrate   - Применить миграции"
	@echo "  make shell     - Django shell"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

test:
	docker compose run --rm web pytest crypto/tests/ -v

lint:
	ruff check .

format:
	ruff format .

migrate:
	docker compose run --rm web python manage.py migrate

shell:
	docker compose run --rm web python manage.py shell
# Crypto Analyzer

API для анализа криптовалют.

## Запуск

Development:
python manage.py runserver

Production:
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3

## Тесты

pytest crypto/tests/ -v

## API Docs

http://127.0.0.1:8000/api/docs/
FROM python:3.12-slim

# Безопасность: создаём не-root пользователя
RUN adduser --disabled-password --gecos "" appuser

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Статика
RUN python manage.py collectstatic --noinput

# Переключаемся на не-root пользователя
USER appuser

# Запускаем Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
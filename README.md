# Crypto Analyzer — Production API

Permissions, Throttling, Swagger, Versioning, Gunicorn

---

### Часть 1: Кастомные permissions

**IsAdminOrReadOnly** (`crypto/permissions.py`)
- SAFE_METHODS (GET, HEAD, OPTIONS) — всем
- POST/PUT/DELETE — только админам (is_staff=True)

**Применение:**
- SnapshotViewSet — ReadOnlyModelViewSet (снимки через Celery)
- FetchSnapshotView — только админы запускают сбор
- Watchlist — IsAuthenticated + filter(user=self.user)

---

### Часть 2: Throttling

| Роль | Лимит |
|------|-------|
| Аноним | 5/мин |
| User | 100/мин |
| Admin | 1000/мин (AdminRateThrottle) |

6 запросов → 429, тест test_throttle_anon_429 подтверждает.

---

### Часть 3: Swagger

- /api/docs/ — Swagger UI
- /api/schema/ — схема
- JWT Authorize кнопка
- @extend_schema с примерами на FetchSnapshotView

---

### Часть 4: Фильтрация и пагинация

- django-filter: CoinPriceFilter (symbol, min_price, max_price)
- SearchFilter: symbol, name
- OrderingFilter: price, change_24h, created_at
- PageNumberPagination: page_size=10
- CursorPagination: /api/v1/coins/

---

### Часть 5: Версионирование

- URLPathVersioning: все под /api/v1/
- Тесты обновлены
- Swagger показывает v1

---

### Часть 6: Единые ошибки

{"error": "message", "code": 401}
400, 401, 403, 404, 429, 500 — единообразно.

---

### Часть 7: Gunicorn + Whitenoise

- Gunicorn: gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
- Whitenoise: WhiteNoiseMiddleware + CompressedManifestStaticFilesStorage
- Статика: python manage.py collectstatic
- README с командами

---

### Тесты

pytest crypto/tests/ -v  # 22 passed

### API Docs

http://127.0.0.1:8000/api/docs/

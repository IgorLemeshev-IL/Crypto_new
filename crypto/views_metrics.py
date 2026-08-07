from django.http import HttpResponse
from prometheus_client import REGISTRY, generate_latest


def metrics_view(request):
    """Эндпоинт для отдачи метрик Prometheus в обход проблем с django_prometheus"""
    metrics_page = generate_latest(REGISTRY)
    return HttpResponse(metrics_page, content_type="text/plain; version=0.0.4; charset=utf-8")

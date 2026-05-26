from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Импортируем нашу новую вьюшку
from crypto.views_metrics import metrics_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("crypto.api.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Добавляем наш собственный маршрут для метрик
    path("metrics/", metrics_view, name="metrics"),
]

urlpatterns += debug_toolbar_urls()

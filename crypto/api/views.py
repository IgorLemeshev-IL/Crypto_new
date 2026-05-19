from celery.result import AsyncResult
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from crypto.analytics_service import AnalyticsService
from crypto.filters import CoinPriceFilter
from crypto.models import CoinPrice, Snapshot
from crypto.permissions import IsAdminOrReadOnly
from crypto.services import WatchlistService
from crypto.tasks import fetch_snapshot_task

from .serializers import CoinPriceSerializer, SnapshotSerializer, WatchlistItemSerializer


class SnapshotViewSet(ReadOnlyModelViewSet):
    queryset = Snapshot.objects.prefetch_related("prices").all()
    serializer_class = SnapshotSerializer
    permission_classes = [IsAdminOrReadOnly]


class CoinPriceViewSet(ReadOnlyModelViewSet):
    queryset = CoinPrice.objects.all()
    serializer_class = CoinPriceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CoinPriceFilter
    search_fields = ["symbol", "name"]
    ordering_fields = ["price", "change_24h"]


class CoinPriceCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-id"


class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = WatchlistService(request.user)
        items = service.list_items()
        serializer = WatchlistItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        symbol = request.data.get("symbol", "")
        service = WatchlistService(request.user)
        try:
            item = service.add_item(symbol)
            serializer = WatchlistItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WatchlistDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, symbol):
        service = WatchlistService(request.user)
        try:
            service.remove_item(symbol)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


class MarketStatsView(APIView):
    def get(self, request):
        data = cache.get("market_stats")
        if data is None:
            stats = AnalyticsService.market_stats()
            if stats is None:
                return Response({"error": "No snapshots"}, status=404)
            data = stats
            cache.set("market_stats", data, timeout=4200)
        return Response(data)


class TopMoversView(APIView):
    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        cache_key = f"top_movers_limit_{limit}"
        data = cache.get(cache_key)  # СНАЧАЛА ПРОВЕРЯЕМ КЭШ
        if data is None:  # Если в кэше нет
            data = AnalyticsService.top_movers(limit)  # ТОГДА считаем
            cache.set(cache_key, data, timeout=4200)  # И сохраняем
        return Response(data)  # Возвращаем из кэша


class VolumeLeadersView(APIView):
    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        cache_key = f"volume_leaders_limit_{limit}"
        data = cache.get(cache_key)
        if data is None:
            data = AnalyticsService.volume_leaders(limit)
            cache.set(cache_key, data, timeout=4200)
        return Response(data)


class CoinsFilterView(APIView):
    def get(self, request):
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        result = AnalyticsService.filter_by_price_range(
            float(min_price) if min_price else None,
            float(max_price) if max_price else None,
        )
        return Response(result)


class FetchSnapshotView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        task = fetch_snapshot_task.delay()
        return Response({"task_id": task.id, "status": "accepted"}, status=status.HTTP_202_ACCEPTED)


class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        response = {
            "task_id": task_id,
            "status": result.state,
        }
        if result.ready():
            if result.successful():
                response["result"] = result.result
            else:
                response["error"] = str(result.info)
        return Response(response)

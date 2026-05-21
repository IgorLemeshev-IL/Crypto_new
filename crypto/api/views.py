from decimal import Decimal

from celery.result import AsyncResult
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from crypto.analytics_service import AnalyticsService
from crypto.filters import CoinPriceFilter
from crypto.models import Balance, CoinPrice, PortfolioPosition, Snapshot
from crypto.permissions import IsAdminOrReadOnly
from crypto.portfolio_service import PortfolioService
from crypto.services import WatchlistService
from crypto.tasks import fetch_snapshot_task

from .serializers import (
    BuySellSerializer,
    CoinPriceSerializer,
    PortfolioPositionSerializer,
    SnapshotSerializer,
    WatchlistItemSerializer,
)


class SnapshotViewSet(ReadOnlyModelViewSet):
    queryset = Snapshot.objects.prefetch_related("prices").all()
    serializer_class = SnapshotSerializer
    permission_classes = [IsAdminOrReadOnly]

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


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
        data = cache.get(cache_key)
        if data is None:
            data = AnalyticsService.top_movers(limit)
            cache.set(cache_key, data, timeout=4200)
        return Response(data)


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


class PortfolioListView(generics.ListAPIView):
    """GET /api/portfolio/ - список позиций портфеля"""

    serializer_class = PortfolioPositionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PortfolioPosition.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        service = PortfolioService(request.user)
        portfolio_data = service.get_portfolio_value()
        return Response(
            {
                "positions": portfolio_data["positions"],
                "total_value": portfolio_data["total_value"],
                "total_invested": portfolio_data["total_invested"],
                "total_profit": portfolio_data["total_profit"],
            }
        )


class PortfolioBuyView(generics.GenericAPIView):
    """POST /api/portfolio/buy/ - покупка монеты"""

    serializer_class = BuySellSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        symbol = serializer.validated_data["symbol"]
        amount = serializer.validated_data["amount"]
        price_per_coin = serializer.validated_data.get("price_per_coin")

        try:
            position = PortfolioService.buy(user=request.user, symbol=symbol, amount=amount, price_per_coin=price_per_coin)

            return Response(
                {
                    "status": "success",
                    "message": f"Successfully bought {amount} {symbol}",
                    "position": {
                        "symbol": position.symbol,
                        "amount": position.amount,
                        "avg_buy_price": position.avg_buy_price,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            raise ValidationError({"detail": str(e)})


class PortfolioSellView(generics.GenericAPIView):
    """POST /api/portfolio/sell/ - продажа монеты"""

    serializer_class = BuySellSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        symbol = serializer.validated_data["symbol"]
        amount = serializer.validated_data["amount"]
        price_per_coin = serializer.validated_data.get("price_per_coin")

        try:
            revenue = PortfolioService.sell(user=request.user, symbol=symbol, amount=amount, price_per_coin=price_per_coin)

            return Response(
                {"status": "success", "message": f"Successfully sold {amount} {symbol}", "revenue": f"${revenue:.2f}"},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            raise ValidationError({"detail": str(e)})


class PortfolioSummaryView(generics.GenericAPIView):
    """GET /api/portfolio/summary/ - сводка по портфелю"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        service = PortfolioService(request.user)
        portfolio_data = service.get_portfolio_value()
        balance, _ = Balance.objects.get_or_create(user=request.user, defaults={"amount": Decimal("0.00")})

        return Response(
            {
                "portfolio": {
                    "total_value": portfolio_data["total_value"],
                    "total_invested": portfolio_data["total_invested"],
                    "total_profit": portfolio_data["total_profit"],
                    "total_profit_percent": (
                        (portfolio_data["total_profit"] / portfolio_data["total_invested"] * 100)
                        if portfolio_data["total_invested"] > 0
                        else 0
                    ),
                },
                "balance_usd": balance.amount,
                "total_net_worth": balance.amount + portfolio_data["total_value"],
            }
        )

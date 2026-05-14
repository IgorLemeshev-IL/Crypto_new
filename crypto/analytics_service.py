from django.db.models import Avg, Max, Min, Q, Sum

from crypto.models import CoinPrice, Snapshot


class AnalyticsService:
    """Сервис аналитики — считает всё через ORM."""

    @staticmethod
    def market_stats():
        """Статистика по последнему снимку."""
        last_snapshot = Snapshot.objects.last()
        if not last_snapshot:
            return None

        stats = CoinPrice.objects.filter(snapshot=last_snapshot).aggregate(
            min_price=Min("price"),
            max_price=Max("price"),
            avg_price=Avg("price"),
            total_cap=Sum("price"),
        )
        return {
            "snapshot_id": last_snapshot.id,
            "created_at": last_snapshot.created_at,
            **stats,
        }

    @staticmethod
    def top_movers(limit: int = 10):
        """Топ-10 по изменению за 24ч в последнем снимке."""
        last_snapshot = Snapshot.objects.last()
        if not last_snapshot:
            return []

        return list(
            CoinPrice.objects.filter(snapshot=last_snapshot)
            .order_by("-change_24h")[:limit]
            .values("name", "symbol", "price", "change_24h")
        )

    @staticmethod
    def volume_leaders(limit: int = 10):
        """Топ-10 по объёму торгов (по цене)."""
        last_snapshot = Snapshot.objects.last()
        if not last_snapshot:
            return []

        return list(
            CoinPrice.objects.filter(snapshot=last_snapshot)
            .order_by("-price")[:limit]
            .values("name", "symbol", "price", "change_24h")
        )

    @staticmethod
    def filter_by_price_range(min_price: float | None = None, max_price: float | None = None):
        """Фильтрация монет по диапазону цен."""
        qs = CoinPrice.objects.all()
        filters = Q()

        if min_price is not None:
            filters &= Q(price__gte=min_price)
        if max_price is not None:
            filters &= Q(price__lte=max_price)

        return list(qs.filter(filters).values("name", "symbol", "price", "change_24h", "snapshot_id"))

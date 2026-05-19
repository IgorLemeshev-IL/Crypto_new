from django.db.models import Avg, Max, Min

from .models import CoinPrice


def calculate_top_movers(snapshot_id):
    coins = CoinPrice.objects.filter(snapshot_id=snapshot_id)
    return list(coins.order_by("-change_24h")[:10].values("name", "symbol", "change_24h"))


def calculate_market_stats(snapshot_id):
    coins = CoinPrice.objects.filter(snapshot_id=snapshot_id)
    stats = coins.aggregate(
        avg_price=Avg("price"),
        max_price=Max("price"),
        min_price=Min("price"),
    )
    return {
        "avg_price": float(stats["avg_price"]) if stats["avg_price"] else None,
        "max_price": float(stats["max_price"]) if stats["max_price"] else None,
        "min_price": float(stats["min_price"]) if stats["min_price"] else None,
        "total_coins": coins.count(),
    }


def calculate_volume_leaders(snapshot_id):
    coins = CoinPrice.objects.filter(snapshot_id=snapshot_id)
    return list(coins.order_by("-price")[:10].values("name", "symbol", "price"))

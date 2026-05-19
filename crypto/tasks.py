import requests
from celery import shared_task
from django.core.cache import cache

from crypto.models import CoinPrice, Snapshot
from crypto.utils import calculate_market_stats, calculate_top_movers, calculate_volume_leaders
from providers.coingecko import CoinGeckoProvider


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def fetch_snapshot_task(self):
    try:
        provider = CoinGeckoProvider(per_page=50)
        assets = provider.get_assets()
    except requests.RequestException as e:
        countdown = 10 * (2**self.request.retries)
        raise self.retry(exc=e, countdown=countdown)

    snapshot = Snapshot.objects.create()
    for asset in assets:
        CoinPrice.objects.create(
            snapshot=snapshot,
            name=asset.name,
            symbol=asset.symbol,
            price=asset.price,
            change_24h=asset.change_24h,
        )

    cache.set("top_movers", calculate_top_movers(snapshot.id), timeout=4200)
    cache.set("market_stats", calculate_market_stats(snapshot.id), timeout=4200)
    cache.set("volume_leaders", calculate_volume_leaders(snapshot.id), timeout=4200)

    return {
        "snapshot_id": snapshot.id,
        "coins_count": len(assets),
    }

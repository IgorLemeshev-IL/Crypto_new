from celery import shared_task
from providers.coingecko import CoinGeckoProvider
from crypto.models import Snapshot, CoinPrice
import requests

# Вынесли логику сбора снимка в отдельную функцию с декоратором @shared_task:
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def fetch_snapshot_task(self):
    """Celery-задача сбора снимка с retry при ошибках API."""
    try:
        provider = CoinGeckoProvider(per_page=50)
        assets = provider.get_assets()
    except requests.RequestException as e:
        # Сетевые ошибки — retry с экспоненциальным backoff
        countdown = 10 * (2 ** self.request.retries)
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

    return {
        'snapshot_id': snapshot.id,
        'coins_count': len(assets),
    }
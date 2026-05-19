import pytest

from crypto.analytics_service import AnalyticsService
from crypto.models import CoinPrice, Snapshot


@pytest.mark.django_db
class TestAnalyticsService:
    def test_empty_stats_returns_none(self):
        assert AnalyticsService.market_stats() is None

    def test_market_stats(self):
        s = Snapshot.objects.create()
        CoinPrice.objects.create(snapshot=s, name="BTC", symbol="btc", price=50000, change_24h=2.5)
        CoinPrice.objects.create(snapshot=s, name="ETH", symbol="eth", price=3000, change_24h=-1.2)

        stats = AnalyticsService.market_stats()
        assert stats["min_price"] == 3000
        assert stats["max_price"] == 50000
        assert stats["total_cap"] == 53000

    def test_top_movers(self):
        s = Snapshot.objects.create()
        CoinPrice.objects.create(snapshot=s, name="BTC", symbol="btc", price=50000, change_24h=5.0)
        CoinPrice.objects.create(snapshot=s, name="ETH", symbol="eth", price=3000, change_24h=-2.0)

        movers = AnalyticsService.top_movers(10)
        assert len(movers) == 2
        assert movers[0]["name"] == "BTC"  # больший change_24h первый

    def test_volume_leaders(self):
        s = Snapshot.objects.create()
        CoinPrice.objects.create(snapshot=s, name="BTC", symbol="btc", price=50000, change_24h=1.0)
        CoinPrice.objects.create(snapshot=s, name="ETH", symbol="eth", price=3000, change_24h=2.0)

        leaders = AnalyticsService.volume_leaders(10)
        assert leaders[0]["name"] == "BTC"  # большая цена = больший объём

    def test_filter_by_price_range(self):
        s = Snapshot.objects.create()
        CoinPrice.objects.create(snapshot=s, name="BTC", symbol="btc", price=50000, change_24h=1.0)
        CoinPrice.objects.create(snapshot=s, name="ETH", symbol="eth", price=3000, change_24h=2.0)

        result = AnalyticsService.filter_by_price_range(min_price=10000, max_price=60000)
        assert len(result) == 1
        assert result[0]["name"] == "BTC"

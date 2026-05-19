import requests

from models.crypto_asset import CryptoAsset
from providers.base import CryptoProvider


class CoinGeckoProvider(CryptoProvider):
    """Провайдер данных с CoinGecko API (бесплатный, без ключа)."""

    BASE_URL = "https://api.coingecko.com"

    def __init__(self, per_page: int = 50):
        self.per_page = per_page

    def get_assets(self) -> list[CryptoAsset]:
        url = f"{self.BASE_URL}/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": self.per_page,
            "page": 1,
        }
        with requests.Session() as session:
            response = session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        assets = []
        for item in data:
            asset = CryptoAsset(
                name=item["name"],
                symbol=item["symbol"],
                price=item["current_price"],
                change_24h=item.get("price_change_percentage_24h") or 0,
                volume=item.get("total_volume") or 0,
            )
            assets.append(asset)

        return assets

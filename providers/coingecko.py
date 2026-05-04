import requests
from providers.base import CryptoProvider
from models.crypto_asset import CryptoAsset


class CoinGeckoProvider(CryptoProvider):
    """Провайдер данных с CoinGecko API (бесплатный, без ключа)."""

    def __init__(self, per_page: int = 50):
        self.per_page = per_page
        self.url = "https://api.coingecko.com/api/v3/coins/markets"

    def get_assets(self) -> list[CryptoAsset]:
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": self.per_page,
            "page": 1,
        }
        with requests.Session() as session:
            response = session.get(self.url, params=params)
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
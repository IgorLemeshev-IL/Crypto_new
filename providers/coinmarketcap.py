import os
import requests
from dotenv import load_dotenv
from providers.base import CryptoProvider
from models.crypto_asset import CryptoAsset

load_dotenv()


class CoinMarketCapProvider(CryptoProvider):
    """Провайдер данных с CoinMarketCap API (требует API-ключ)."""

    def __init__(self):
        self.api_key = os.getenv("CMC_API_KEY")
        self.url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    def get_assets(self) -> list[CryptoAsset]:
        headers = {"X-CMC_PRO_API_KEY": self.api_key}
        params = {"limit": 50, "convert": "USD"}

        response = requests.get(self.url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()["data"]

        assets = []
        for item in data:
            quote = item["quote"]["USD"]
            asset = CryptoAsset(
                name=item["name"],
                symbol=item["symbol"],
                price=quote["price"],
                change_24h=quote.get("percent_change_24h") or 0,
            )
            assets.append(asset)

        return assets
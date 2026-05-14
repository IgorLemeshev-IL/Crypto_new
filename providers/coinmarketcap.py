import requests

from models.crypto_asset import CryptoAsset
from providers.base import CryptoProvider
from settings import Settings


class CoinMarketCapProvider(CryptoProvider):
    BASE_URL = "https://pro-api.coinmarketcap.com"

    def __init__(self):
        self.api_key = Settings.get_cmc_api_key()

    def get_assets(self) -> list[CryptoAsset]:
        url = f"{self.BASE_URL}/v1/cryptocurrency/listings/latest"
        headers = {"X-CMC_PRO_API_KEY": self.api_key}
        params: dict[str, str | int] = {"limit": 50, "convert": "USD"}
        with requests.Session() as session:
            response = session.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()["data"]

        assets = []
        for item in data:
            quote = item["quote"]["USD"]
            assets.append(
                CryptoAsset(
                    name=item["name"],
                    symbol=item["symbol"],
                    price=quote["price"],
                    change_24h=quote.get("percent_change_24h") or 0,
                    volume=quote.get("volume_24h") or 0,
                )
            )
        return assets

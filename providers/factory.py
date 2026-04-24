from providers.coingecko import CoinGeckoProvider
from providers.coinmarketcap import CoinMarketCapProvider
from providers.base import CryptoProvider


class ProviderFactory:
    """Фабрика провайдеров — создаёт нужный провайдер по имени."""

    @staticmethod
    def create(name: str) -> CryptoProvider:
        if name == "coingecko":
            return CoinGeckoProvider()
        if name == "coinmarketcap":
            return CoinMarketCapProvider()
        raise ValueError(f"Unknown provider: {name}")
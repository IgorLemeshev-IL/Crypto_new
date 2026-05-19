from providers.factory import ProviderFactory
from providers.coingecko import CoinGeckoProvider
from providers.coinmarketcap import CoinMarketCapProvider

ProviderFactory.register("coingecko", CoinGeckoProvider)
ProviderFactory.register("coinmarketcap", CoinMarketCapProvider)
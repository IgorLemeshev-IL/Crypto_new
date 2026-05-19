from providers.coingecko import CoinGeckoProvider
from providers.coinmarketcap import CoinMarketCapProvider
from providers.factory import ProviderFactory

ProviderFactory.register("coingecko", CoinGeckoProvider)
ProviderFactory.register("coinmarketcap", CoinMarketCapProvider)

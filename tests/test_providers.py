import pytest
from unittest.mock import Mock, MagicMock
from unittest.mock import patch

from providers.coingecko import CoinGeckoProvider
from providers.coinmarketcap import CoinMarketCapProvider
from providers.base import CryptoProvider
from models.crypto_asset import CryptoAsset


class TestCoinGeckoProvider:
    """Тесты CoinGecko провайдера."""

    def test_get_assets_success(self, mock_session, mock_coingecko_response):
        provider = CoinGeckoProvider()
        assets = provider.get_assets()

        assert len(assets) == 3
        assert assets[0].name == "Bitcoin"
        assert isinstance(assets[0], CryptoAsset)

    def test_inherits_from_crypto_provider(self):
        provider = CoinGeckoProvider()
        assert isinstance(provider, CryptoProvider)

    def test_empty_response(self):
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None

            provider = CoinGeckoProvider()
            assets = provider.get_assets()
            assert assets == []


class TestCoinMarketCapProvider:
    """Тесты CoinMarketCap провайдера."""

    def test_get_assets_success(self, mock_session_cmc, mock_cmc_response):
        provider = CoinMarketCapProvider()
        assets = provider.get_assets()

        assert len(assets) == 3
        assert assets[0].name == "Bitcoin"
        assert isinstance(assets[0], CryptoAsset)

    def test_inherits_from_crypto_provider(self):
        provider = CoinMarketCapProvider()
        assert isinstance(provider, CryptoProvider)

    def test_missing_quote_field(self):
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.json.return_value = {"data": [{"name": "BTC", "symbol": "BTC"}]}
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None

            provider = CoinMarketCapProvider()
            with pytest.raises(KeyError):
                provider.get_assets() 


class TestProviderFactory:
    """Тесты фабрики провайдеров."""

    def test_create_coingecko(self):
        from providers.factory import ProviderFactory
        provider = ProviderFactory.create("coingecko")
        assert isinstance(provider, CoinGeckoProvider)

    def test_create_coinmarketcap(self):
        from providers.factory import ProviderFactory
        provider = ProviderFactory.create("coinmarketcap")
        assert isinstance(provider, CoinMarketCapProvider)

    def test_unknown_provider(self):
        from providers.factory import ProviderFactory
        with pytest.raises(ValueError, match="Unknown provider"):
            ProviderFactory.create("binance")
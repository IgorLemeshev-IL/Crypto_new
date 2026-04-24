import pytest
from unittest.mock import Mock

from providers.coingecko import CoinGeckoProvider
from providers.coinmarketcap import CoinMarketCapProvider
from providers.base import CryptoProvider
from models.crypto_asset import CryptoAsset


class TestCoinGeckoProvider:
    """Тесты CoinGecko провайдера."""

    def test_get_assets_success(self, mock_requests_get, mock_coingecko_response):
        mock_response = Mock()
        mock_response.json.return_value = mock_coingecko_response
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value.__enter__.return_value = mock_response

        provider = CoinGeckoProvider()
        assets = provider.get_assets()

        assert len(assets) == 3
        assert assets[0].name == "Bitcoin"
        assert isinstance(assets[0], CryptoAsset)

    def test_inherits_from_crypto_provider(self):
        provider = CoinGeckoProvider()
        assert isinstance(provider, CryptoProvider)

    def test_empty_response(self, mock_requests_get):
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value.__enter__.return_value = mock_response

        provider = CoinGeckoProvider()
        assets = provider.get_assets()
        assert assets == []


class TestCoinMarketCapProvider:
    """Тесты CoinMarketCap провайдера."""

    def test_get_assets_success(self, mock_requests_get, mock_cmc_response):
        mock_response = Mock()
        mock_response.json.return_value = mock_cmc_response
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value.__enter__.return_value = mock_response

        provider = CoinMarketCapProvider()
        assets = provider.get_assets()

        assert len(assets) == 3
        assert assets[0].name == "Bitcoin"
        assert isinstance(assets[0], CryptoAsset)

    def test_inherits_from_crypto_provider(self):
        provider = CoinMarketCapProvider()
        assert isinstance(provider, CryptoProvider)

    def test_missing_quote_field(self, mock_requests_get):
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"name": "BTC", "symbol": "BTC"}]}
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value.__enter__.return_value = mock_response

        provider = CoinMarketCapProvider()
        with pytest.raises(KeyError):
            provider.get_assets()
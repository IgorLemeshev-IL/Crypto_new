from unittest.mock import MagicMock, Mock, patch

import pytest

from models.crypto_asset import CryptoAsset

# ========== ТЕСТОВЫЕ ДАННЫЕ ==========


@pytest.fixture
def sample_asset():
    return CryptoAsset(name="Bitcoin", symbol="BTC", price=50000.0, change_24h=2.5)


@pytest.fixture
def sample_assets_list():
    return [
        CryptoAsset(name="Bitcoin", symbol="BTC", price=50000.0, change_24h=2.5),
        CryptoAsset(name="Ethereum", symbol="ETH", price=3000.0, change_24h=-1.2),
        CryptoAsset(name="Solana", symbol="SOL", price=100.0, change_24h=5.8),
        CryptoAsset(name="Cardano", symbol="ADA", price=0.5, change_24h=-3.1),
        CryptoAsset(name="Ripple", symbol="XRP", price=0.8, change_24h=0.5),
    ]


# ========== MOCK ОТВЕТЫ API ==========


@pytest.fixture
def mock_coingecko_response():
    return [
        {
            "name": "Bitcoin",
            "symbol": "btc",
            "current_price": 50000.0,
            "price_change_percentage_24h": 2.5,
        },
        {
            "name": "Ethereum",
            "symbol": "eth",
            "current_price": 3000.0,
            "price_change_percentage_24h": -1.2,
        },
        {
            "name": "Solana",
            "symbol": "sol",
            "current_price": 100.0,
            "price_change_percentage_24h": 5.8,
        },
    ]


@pytest.fixture
def mock_cmc_response():
    return {
        "data": [
            {
                "name": "Bitcoin",
                "symbol": "BTC",
                "quote": {"USD": {"price": 50000.0, "percent_change_24h": 2.5}},
            },
            {
                "name": "Ethereum",
                "symbol": "ETH",
                "quote": {"USD": {"price": 3000.0, "percent_change_24h": -1.2}},
            },
            {
                "name": "Solana",
                "symbol": "SOL",
                "quote": {"USD": {"price": 100.0, "percent_change_24h": 5.8}},
            },
        ]
    }


# ========== MOCK HTTP С SESSION ==========


@pytest.fixture
def mock_session(mock_coingecko_response):
    """Мок requests.Session."""
    with patch("requests.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_coingecko_response
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None
        yield mock_session


@pytest.fixture
def mock_session_cmc(mock_cmc_response):
    """Мок requests.Session для CMC."""
    with patch("requests.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_cmc_response
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None
        yield mock_session

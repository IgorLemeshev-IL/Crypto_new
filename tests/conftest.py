import pytest
from unittest.mock import Mock, patch
import os

from models.crypto_asset import CryptoAsset


# ========== ТЕСТОВЫЕ ДАННЫЕ ==========

@pytest.fixture
def sample_asset():
    """Одиночный тестовый актив."""
    return CryptoAsset(name="Bitcoin", symbol="BTC", price=50000.0, change_24h=2.5)


@pytest.fixture
def sample_assets_list():
    """Список из 5 тестовых активов."""
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
    """Мок-ответ CoinGecko API."""
    return [
        {"name": "Bitcoin", "symbol": "btc", "current_price": 50000.0, "price_change_percentage_24h": 2.5},
        {"name": "Ethereum", "symbol": "eth", "current_price": 3000.0, "price_change_percentage_24h": -1.2},
        {"name": "Solana", "symbol": "sol", "current_price": 100.0, "price_change_percentage_24h": 5.8},
    ]


@pytest.fixture
def mock_cmc_response():
    """Мок-ответ CoinMarketCap API."""
    return {
        "data": [
            {"name": "Bitcoin", "symbol": "BTC", "quote": {"USD": {"price": 50000.0, "percent_change_24h": 2.5}}},
            {"name": "Ethereum", "symbol": "ETH", "quote": {"USD": {"price": 3000.0, "percent_change_24h": -1.2}}},
            {"name": "Solana", "symbol": "SOL", "quote": {"USD": {"price": 100.0, "percent_change_24h": 5.8}}},
        ]
    }


# ========== MOCK HTTP ==========

@pytest.fixture
def mock_requests_get():
    """Мок requests.get — возвращает настраиваемый ответ."""
    with patch("requests.get") as mock_get:
        yield mock_get
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connections
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from models.crypto_asset import CryptoAsset

# ========== СТАРЫЕ ФИКСТУРЫ ==========


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


@pytest.fixture
def mock_session(mock_coingecko_response):
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
    with patch("requests.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_cmc_response
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None
        yield mock_session


# ========== НОВЫЕ ФИКСТУРЫ ДЛЯ DJANGO ТЕСТОВ ==========


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7") as redis:
        yield redis


@pytest.fixture(scope="session")
def django_db_setup(postgres_container):
    from django.conf import settings

    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": postgres_container.dbname,
        "USER": postgres_container.username,
        "PASSWORD": postgres_container.password,
        "HOST": postgres_container.get_container_host_ip(),
        "PORT": postgres_container.get_exposed_port(5432),
    }

    call_command("migrate")
    yield

    for conn in connections.all():
        conn.close()


@pytest.fixture
def redis_client(redis_container):
    import redis

    client = redis.Redis(
        host=redis_container.get_container_host_ip(), port=redis_container.get_exposed_port(6379), decode_responses=True
    )
    yield client


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def authenticated_client(client, test_user):
    client.force_login(test_user)
    return client

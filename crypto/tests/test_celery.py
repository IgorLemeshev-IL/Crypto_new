from unittest.mock import patch

import pytest
from celery.exceptions import Retry


class FakeAsset:
    def __init__(self, name, symbol, price, change_24h):
        self.name = name
        self.symbol = symbol
        self.price = price
        self.change_24h = change_24h


@pytest.mark.django_db
class TestCeleryTask:
    def test_fetch_snapshot_success(self):
        from crypto.tasks import fetch_snapshot_task

        mock_assets = [
            FakeAsset("Bitcoin", "btc", 50000, 2.5),
            FakeAsset("Ethereum", "eth", 3000, -1.2),
        ]
        with patch("crypto.tasks.CoinGeckoProvider") as MockProvider:
            MockProvider.return_value.get_assets.return_value = mock_assets
            result = fetch_snapshot_task.run()

        assert result["coins_count"] == 2
        assert result["snapshot_id"] is not None

    def test_fetch_snapshot_retry_on_error(self):
        import requests

        from crypto.tasks import fetch_snapshot_task

        with (
            patch("crypto.tasks.CoinGeckoProvider") as MockProvider,
            patch.object(fetch_snapshot_task, "retry", side_effect=Retry("API Error")) as mock_retry,
        ):
            MockProvider.return_value.get_assets.side_effect = requests.RequestException("API Error")

            with pytest.raises(Retry):
                fetch_snapshot_task.run()

            mock_retry.assert_called_once()


@pytest.mark.django_db
class TestTaskAPI:
    def test_fetch_snapshot_returns_202(self, client):
        response = client.post("/api/tasks/fetch-snapshot/")
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "accepted"

    def test_task_status_pending(self, client):
        response = client.get("/api/tasks/non-existent-id/")
        assert response.status_code == 200
        assert response.json()["status"] == "PENDING"

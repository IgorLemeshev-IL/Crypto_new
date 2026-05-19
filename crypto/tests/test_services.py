from unittest.mock import patch

import pytest
from django.contrib.auth.models import User

from crypto.services import WatchlistService


@pytest.mark.django_db
class TestWatchlistService:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="testuser", password="pass")

    @pytest.fixture
    def service(self, user):
        return WatchlistService(user)

    def test_list_empty(self, service):
        assert service.list_items().count() == 0

    def test_add_item_success(self, service):
        with patch.object(service, "_validate_symbol"):
            item = service.add_item("BTC")
            assert item.symbol == "BTC"
            assert service.list_items().count() == 1

    def test_add_duplicate_raises_error(self, service):
        with patch.object(service, "_validate_symbol"):
            service.add_item("BTC")
            with pytest.raises(ValueError, match="уже в watchlist"):
                service.add_item("BTC")

    def test_add_invalid_symbol_raises_error(self, service):
        with patch.object(service, "_validate_symbol", side_effect=ValueError("не найден")):
            with pytest.raises(ValueError, match="не найден"):
                service.add_item("XXX")

    def test_remove_item_success(self, service):
        with patch.object(service, "_validate_symbol"):
            service.add_item("BTC")
        service.remove_item("BTC")
        assert service.list_items().count() == 0

    def test_remove_not_found_raises_error(self, service):
        with pytest.raises(ValueError, match="нет в watchlist"):
            service.remove_item("XXX")

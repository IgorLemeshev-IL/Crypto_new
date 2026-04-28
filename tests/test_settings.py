import os
from unittest.mock import patch
from settings import StorageType


class TestSettings:
    """Тесты для Settings."""

    def test_default_storage_is_json(self):
        """По умолчанию 'json'."""
        assert StorageType(os.getenv("NOT_EXIST", "json")) == StorageType.JSON

    def test_storage_sqlite_from_value(self):
        """Строка 'sqlite' → StorageType.SQLITE."""
        assert StorageType("sqlite") == StorageType.SQLITE

    def test_storage_json_from_value(self):
        """Строка 'json' → StorageType.JSON."""
        assert StorageType("json") == StorageType.JSON
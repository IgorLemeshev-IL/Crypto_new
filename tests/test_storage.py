import pytest

from storage.sqlite_storage import SqliteStorage


class TestSqliteStorage:
    """Тесты SqliteStorage на БД в памяти."""

    @pytest.fixture
    def storage(self):
        """Создаёт хранилище с БД в памяти."""
        return SqliteStorage(db_path=":memory:")

    def test_save_creates_snapshot(self, storage, sample_asset):
        """save() создаёт запись, используя sample_asset из conftest."""
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": sample_asset.name,
                        "symbol": sample_asset.symbol,
                        "price": sample_asset.price,
                        "change_24h": sample_asset.change_24h,
                    }
                ]
            }
        )
        snapshots = storage.list_snapshots()
        assert len(snapshots) == 1

    def test_save_creates_coin_prices(self, storage, sample_assets_list):
        """save() создаёт записи из sample_assets_list (conftest)."""
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": a.name,
                        "symbol": a.symbol,
                        "price": a.price,
                        "change_24h": a.change_24h,
                    }
                    for a in sample_assets_list[:2]
                ]
            }
        )
        movers = storage.top_movers(10)
        assert len(movers) == 2

    def test_save_twice_creates_two_snapshots(self, storage, sample_asset):
        """Два save() = два снимка, используется sample_asset."""
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": sample_asset.name,
                        "symbol": sample_asset.symbol,
                        "price": 100.0,
                        "change_24h": 1.0,
                    }
                ]
            }
        )
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": sample_asset.name,
                        "symbol": sample_asset.symbol,
                        "price": 200.0,
                        "change_24h": 2.0,
                    }
                ]
            }
        )
        assert len(storage.list_snapshots()) == 2

    def test_compare_snapshots(self, storage, sample_asset):
        """compare через self-JOIN с sample_asset."""
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": sample_asset.name,
                        "symbol": sample_asset.symbol,
                        "price": 100.0,
                        "change_24h": 1.0,
                    }
                ]
            }
        )
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": sample_asset.name,
                        "symbol": sample_asset.symbol,
                        "price": 200.0,
                        "change_24h": 2.0,
                    }
                ]
            }
        )
        result = storage.compare_snapshots(1, 2)
        assert len(result) == 1
        assert result[0]["price_old"] == 100.0
        assert result[0]["price_new"] == 200.0

    def test_history(self, storage, sample_asset):
        """history через JOIN с sample_asset."""
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": sample_asset.name,
                        "symbol": sample_asset.symbol,
                        "price": 100.0,
                        "change_24h": 1.0,
                    }
                ]
            }
        )
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": sample_asset.name,
                        "symbol": sample_asset.symbol,
                        "price": 200.0,
                        "change_24h": 2.0,
                    }
                ]
            }
        )
        history = storage.history(sample_asset.name)
        assert len(history) == 2

    def test_top_movers(self, storage, sample_assets_list):
        """top_movers с sample_assets_list."""
        storage.save(
            {
                "top_gainers": [
                    {
                        "name": a.name,
                        "symbol": a.symbol,
                        "price": a.price,
                        "change_24h": a.change_24h,
                    }
                    for a in sample_assets_list[:2]
                ]
            }
        )
        movers = storage.top_movers(2)
        assert movers[0]["name"] == sample_assets_list[0].name

    def test_empty_storage(self, storage):
        """Пустое хранилище."""
        assert storage.list_snapshots() == []
        assert storage.top_movers() == []


class TestStorageFactory:
    """Тесты фабрики хранилищ."""

    def test_create_json_storage(self):
        from storage.factory import StorageFactory
        from storage.json_storage import JsonStorage

        storage = StorageFactory.create_by_name("json")
        assert isinstance(storage, JsonStorage)

    def test_create_sqlite_storage(self):
        from storage.factory import StorageFactory
        from storage.sqlite_storage import SqliteStorage

        storage = StorageFactory.create_by_name("sqlite")
        assert isinstance(storage, SqliteStorage)

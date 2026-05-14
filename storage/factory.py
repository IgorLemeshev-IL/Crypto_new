from settings import Settings
from storage.base import BaseStorage
from storage.json_storage import JsonStorage
from storage.sqlite_storage import SqliteStorage


class StorageFactory:
    """Фабрика хранилищ."""

    @staticmethod
    def create(settings: Settings) -> BaseStorage:
        return StorageFactory.create_by_name(settings.storage.value)

    @staticmethod
    def create_by_name(name: str) -> BaseStorage:
        if name == "json":
            return JsonStorage()
        if name == "sqlite":
            return SqliteStorage()
        raise ValueError(f"Unknown storage type: {name}")

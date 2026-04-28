from settings import Settings, StorageType
from storage.base import BaseStorage
from storage.json_storage import JsonStorage


class StorageFactory:
    """Фабрика хранилищ — создаёт нужное хранилище по настройкам."""

    @staticmethod
    def create(settings: Settings) -> BaseStorage:
        if settings.storage == StorageType.JSON:
            return JsonStorage()
        raise ValueError(f"Unknown storage type: {settings.storage}")
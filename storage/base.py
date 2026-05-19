from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """Базовый интерфейс для всех хранилищ."""

    @abstractmethod
    def save(self, results: dict) -> None:
        """Сохраняет результаты анализа."""
        pass

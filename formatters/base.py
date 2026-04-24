from abc import ABC, abstractmethod
from models.crypto_asset import CryptoAsset


class OutputFormatter(ABC):
    """Базовый интерфейс для всех форматов вывода."""

    @abstractmethod
    def format(self, assets: list[CryptoAsset]) -> None:
        """Выводит список активов в нужном формате."""
        pass
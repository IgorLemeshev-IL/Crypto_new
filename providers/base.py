from abc import ABC, abstractmethod
from models.crypto_asset import CryptoAsset


class CryptoProvider(ABC):
    """Базовый интерфейс для всех крипто-провайдеров."""

    @abstractmethod
    def get_assets(self) -> list[CryptoAsset]:
        """Должен вернуть список CryptoAsset."""
        pass
from abc import ABC, abstractmethod

from models.crypto_asset import CryptoAsset


class OutputFormatter(ABC):
    @abstractmethod
    def format(self, gainers: list[CryptoAsset], losers: list[CryptoAsset]) -> None:
        pass

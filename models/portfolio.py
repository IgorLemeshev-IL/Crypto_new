from models.crypto_asset import CryptoAsset


class CryptoPortfolio:
    """Коллекция криптоактивов с методами анализа."""

    def __init__(self, assets: list[CryptoAsset]):
        self.assets = assets

    def top_gainers(self, n: int = 3) -> list[CryptoAsset]:
        """Топ-n лидеров роста."""
        return sorted(self.assets, key=lambda x: x.change_24h, reverse=True)[:n]

    def top_losers(self, n: int = 3) -> list[CryptoAsset]:
        """Топ-n лидеров падения."""
        return sorted(self.assets, key=lambda x: x.change_24h)[:n]

    def highest_volume(self) -> CryptoAsset:
        """Актив с максимальным объёмом торгов."""
        return max(self.assets, key=lambda x: x.volume)

    def total_value(self) -> float:
        """Суммарная стоимость всех активов."""
        return sum(a.price for a in self.assets)

    def filter_positive(self) -> list[CryptoAsset]:
        """Только растущие активы."""
        return [a for a in self.assets if a.change_24h > 0]

    def filter_negative(self) -> list[CryptoAsset]:
        """Только падающие активы."""
        return [a for a in self.assets if a.change_24h < 0]

    def __len__(self):
        return len(self.assets)

    def __iter__(self):
        return iter(self.assets)

    def __getitem__(self, index):
        return self.assets[index]

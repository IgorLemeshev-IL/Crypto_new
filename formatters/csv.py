import csv
import sys
from models.crypto_asset import CryptoAsset
from formatters.base import OutputFormatter


class CSVFormatter(OutputFormatter):
    """Вывод результатов в формате CSV."""

    def format(self, assets: list[CryptoAsset]) -> None:
        writer = csv.writer(sys.stdout)
        writer.writerow(["name", "symbol", "price", "change_24h"])
        for a in assets:
            writer.writerow([a.name, a.symbol, a.price, a.change_24h])
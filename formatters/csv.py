import csv
import sys

from formatters.base import OutputFormatter
from models.crypto_asset import CryptoAsset


class CSVFormatter(OutputFormatter):
    def format(self, gainers: list[CryptoAsset], losers: list[CryptoAsset]) -> None:
        writer = csv.writer(sys.stdout)
        writer.writerow(["type", "name", "symbol", "price", "change_24h"])
        for a in gainers:
            writer.writerow(["gainer", a.name, a.symbol, a.price, a.change_24h])
        for a in losers:
            writer.writerow(["loser", a.name, a.symbol, a.price, a.change_24h])

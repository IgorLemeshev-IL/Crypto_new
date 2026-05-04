import json
from models.crypto_asset import CryptoAsset
from formatters.base import OutputFormatter


class JSONFormatter(OutputFormatter):
    def format(self, gainers: list[CryptoAsset], losers: list[CryptoAsset]) -> None:
        data = {
            "top_gainers": [
                {"name": a.name, "symbol": a.symbol, "price": a.price, "change_24h": a.change_24h}
                for a in gainers
            ],
            "top_losers": [
                {"name": a.name, "symbol": a.symbol, "price": a.price, "change_24h": a.change_24h}
                for a in losers
            ]
        }
        print(json.dumps(data, indent=4, ensure_ascii=False))

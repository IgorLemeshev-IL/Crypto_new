import json
from models.crypto_asset import CryptoAsset
from formatters.base import OutputFormatter


class JSONFormatter(OutputFormatter):
    """Вывод результатов в формате JSON."""

    def format(self, assets: list[CryptoAsset]) -> None:
        data = [
            {
                "name": a.name,
                "symbol": a.symbol,
                "price": a.price,
                "change_24h": a.change_24h,
            }
            for a in assets
        ]
        print(json.dumps(data, indent=4, ensure_ascii=False))
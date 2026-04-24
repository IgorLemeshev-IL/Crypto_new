class CryptoAsset:
    """Класс одной криптовалюты. Инкапсулирует все данные об активе."""

    def __init__(self, name: str, symbol: str, price: float, change_24h: float):
        # Валидация
        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol must be a non-empty string")
        if not isinstance(price, (int, float)):
            raise TypeError("price must be a number")
        if not isinstance(change_24h, (int, float)):
            raise TypeError("change_24h must be a number")

        self.name = name
        self.symbol = symbol
        self.price = price
        self.change_24h = change_24h

    def __str__(self):
        return f"{self.name} ({self.symbol}): ${self.price:.2f} ({self.change_24h:+.2f}%)"

    def __repr__(self):
        return (
            f"CryptoAsset(name={self.name}, "
            f"symbol={self.symbol}, "
            f"price={self.price}, "
            f"change_24h={self.change_24h})"
        )

    def __lt__(self, other):
        if not isinstance(other, CryptoAsset):
            return NotImplemented
        return self.change_24h < other.change_24h

    def __gt__(self, other):
        if not isinstance(other, CryptoAsset):
            return NotImplemented
        return self.change_24h > other.change_24h
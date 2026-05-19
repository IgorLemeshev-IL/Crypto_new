class CryptoAsset:
    """Класс одной криптовалюты."""

    def __init__(self, name: str, symbol: str, price: float, change_24h: float, volume: float = 0.0):
        self._validate_str(name, "name")
        self._validate_str(symbol, "symbol")
        self._validate_number(price, "price")
        self._validate_number(change_24h, "change_24h")
        self._validate_number(volume, "volume")

        self.name = name
        self.symbol = symbol
        self.price = price
        self.change_24h = change_24h
        self.volume = volume

    @staticmethod
    def _validate_str(value, field_name):
        if not value or not isinstance(value, str):
            raise ValueError(f"{field_name} must be a non-empty string")

    @staticmethod
    def _validate_number(value, field_name):
        if not isinstance(value, int | float):
            raise TypeError(f"{field_name} must be a number")

    def __str__(self):
        return f"{self.name} ({self.symbol}): ${self.price:.2f} ({self.change_24h:+.2f}%)"

    def __repr__(self):
        return f"CryptoAsset(name={self.name}, symbol={self.symbol}, price={self.price}, change_24h={self.change_24h})"

    def __lt__(self, other):
        if not isinstance(other, CryptoAsset):
            return NotImplemented
        return self.change_24h < other.change_24h

    def __gt__(self, other):
        if not isinstance(other, CryptoAsset):
            return NotImplemented
        return self.change_24h > other.change_24h

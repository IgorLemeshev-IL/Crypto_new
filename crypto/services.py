from providers.factory import ProviderFactory
from crypto.models import WatchlistItem
from django.contrib.auth.models import User


class WatchlistService:
    """Сервис для работы с watchlist. Не знает ничего про DRF."""

    def __init__(self, user: User):
        self.user = user

    def list_items(self):
        """Возвращает список отслеживаемых символов."""
        return WatchlistItem.objects.filter(user=self.user)

    def add_item(self, symbol: str):
        """Добавляет символ в watchlist. Валидирует через биржу."""
        symbol = symbol.upper().strip()

        # Проверка что уже есть
        if WatchlistItem.objects.filter(user=self.user, symbol=symbol).exists():
            raise ValueError(f"{symbol} уже в watchlist")

        # Валидация через биржу
        self._validate_symbol(symbol)

        return WatchlistItem.objects.create(user=self.user, symbol=symbol)

    def remove_item(self, symbol: str):
        """Удаляет символ из watchlist."""
        symbol = symbol.upper().strip()
        deleted, _ = WatchlistItem.objects.filter(
            user=self.user, symbol=symbol
        ).delete()
        if deleted == 0:
            raise ValueError(f"{symbol} нет в watchlist")

    def _validate_symbol(self, symbol: str):
        """Проверяет существование символа через API биржи."""
        provider = ProviderFactory.create("coingecko")
        assets = provider.get_assets()
        valid_symbols = {a.symbol.upper() for a in assets}
        if symbol not in valid_symbols:
            raise ValueError(f"Символ {symbol} не найден на бирже")
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction

from crypto.models import Balance, CoinPrice, PortfolioPosition, Snapshot


class PortfolioService:
    """Сервис для работы с портфелем. Не знает ничего про DRF."""

    def __init__(self, user: User):
        self.user = user

    @staticmethod
    def _get_current_price(symbol: str) -> Decimal:
        """
        Получить текущую цену монеты из последнего снимка.
        Использует Snapshot модель (как в watchlist используется биржа).
        """
        last_snapshot = Snapshot.objects.last()
        if not last_snapshot:
            raise ValueError("No market snapshot available")

        try:
            coin_price = CoinPrice.objects.get(snapshot=last_snapshot, symbol=symbol)
            return Decimal(str(coin_price.price))
        except CoinPrice.DoesNotExist:
            raise ValueError(f"Price for {symbol} not found in latest snapshot")

    @classmethod
    @transaction.atomic
    def buy(cls, user: User, symbol: str, amount: Decimal, price_per_coin: Decimal = None):
        """
        Атомарная покупка монеты.

        Если price_per_coin не указан, берётся из последнего снимка.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        symbol = symbol.upper().strip()

        # Получаем цену
        if price_per_coin is None:
            price_per_coin = cls._get_current_price(symbol)
        else:
            price_per_coin = Decimal(str(price_per_coin))

        # Рассчитываем стоимость покупки
        cost = amount * price_per_coin

        # БЛОКИРУЕМ баланс для этой транзакции (select_for_update)
        try:
            balance = Balance.objects.select_for_update().get(user=user)
        except Balance.DoesNotExist:
            # Если баланса нет — создаём с нулём
            balance = Balance.objects.create(user=user, amount=Decimal("0.00"))
            balance = Balance.objects.select_for_update().get(user=user)

        # Проверяем достаточно ли средств
        if balance.amount < cost:
            raise ValueError(f"Insufficient balance. Required: ${cost:.2f}, available: ${balance.amount:.2f}")

        # Списываем баланс
        balance.amount -= cost
        balance.save(update_fields=["amount"])

        # Обновляем или создаём позицию в портфеле
        position, created = PortfolioPosition.objects.select_for_update().get_or_create(
            user=user,
            symbol=symbol,
            defaults={
                "amount": amount,
                "avg_buy_price": price_per_coin,
            },
        )

        if not created:
            # Уже есть позиция — пересчитываем среднюю цену
            total_amount = position.amount + amount
            total_cost = (position.amount * position.avg_buy_price) + cost
            position.avg_buy_price = total_cost / total_amount
            position.amount = total_amount
            position.save(update_fields=["amount", "avg_buy_price"])

        return position

    @classmethod
    @transaction.atomic
    def sell(cls, user: User, symbol: str, amount: Decimal, price_per_coin: Decimal = None):
        """
        Атомарная продажа монеты.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        symbol = symbol.upper().strip()

        # Получаем цену
        if price_per_coin is None:
            price_per_coin = cls._get_current_price(symbol)
        else:
            price_per_coin = Decimal(str(price_per_coin))

        # БЛОКИРУЕМ позицию
        try:
            position = PortfolioPosition.objects.select_for_update().get(user=user, symbol=symbol)
        except PortfolioPosition.DoesNotExist:
            raise ValueError(f"No position for {symbol} found in portfolio")

        if position.amount < amount:
            raise ValueError(f"Insufficient amount. Have {position.amount:.8f} {symbol}, want to sell {amount:.8f}")

        # Рассчитываем выручку
        revenue = amount * price_per_coin

        # Обновляем или удаляем позицию
        if position.amount == amount:
            position.delete()
        else:
            position.amount -= amount
            position.save(update_fields=["amount"])

        # Зачисляем баланс (с блокировкой)
        balance, _ = Balance.objects.select_for_update().get_or_create(user=user, defaults={"amount": Decimal("0.00")})
        balance.amount += revenue
        balance.save(update_fields=["amount"])

        return revenue

    def get_portfolio_value(self) -> dict:
        """
        Получить текущую стоимость портфеля и прибыль/убыток.
        """
        positions = PortfolioPosition.objects.filter(user=self.user)

        if not positions:
            return {
                "total_value": Decimal("0.00"),
                "total_invested": Decimal("0.00"),
                "total_profit": Decimal("0.00"),
                "positions": [],
            }

        total_value = Decimal("0.00")
        total_invested = Decimal("0.00")
        positions_data = []

        for position in positions:
            try:
                current_price = self._get_current_price(position.symbol)
            except ValueError:
                current_price = position.avg_buy_price

            current_value = position.amount * current_price
            invested = position.amount * position.avg_buy_price
            profit = current_value - invested

            total_value += current_value
            total_invested += invested

            positions_data.append(
                {
                    "symbol": position.symbol,
                    "amount": position.amount,
                    "avg_buy_price": position.avg_buy_price,
                    "current_price": current_price,
                    "current_value": current_value,
                    "invested": invested,
                    "profit": profit,
                    "profit_percent": (profit / invested * 100) if invested > 0 else 0,
                }
            )

        return {
            "total_value": total_value,
            "total_invested": total_invested,
            "total_profit": total_value - total_invested,
            "positions": positions_data,
        }

from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class Snapshot(models.Model):
    """Снимок рынка — фиксирует момент времени."""

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # новые сверху

    def __str__(self):
        return f"Снимок от {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class CoinPrice(models.Model):
    """Цена монеты в конкретном снимке."""

    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, related_name="prices")
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=50)
    price = models.FloatField()
    change_24h = models.FloatField()

    class Meta:
        ordering = ["-change_24h"]  # по убыванию изменения

    def __str__(self):
        return f"{self.name} ({self.symbol}) — ${self.price}"


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    symbol = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "symbol")  # нельзя добавить одну монету дважды
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.symbol}"


class Balance(models.Model):
    """Баланс пользователя в USD."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="crypto_balance")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Balance"
        verbose_name_plural = "Balances"

    def __str__(self):
        return f"{self.user.username}: ${self.amount}"


class PortfolioPosition(models.Model):
    """Позиция портфеля пользователя по конкретной монете."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolio_positions")
    symbol = models.CharField(max_length=50)  # BTC, ETH и т.д.
    amount = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal("0.00000000"))
    avg_buy_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Средняя цена покупки в USD")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["user", "symbol"]]
        verbose_name = "Portfolio position"
        verbose_name_plural = "Portfolio positions"
        indexes = [
            models.Index(fields=["user", "symbol"]),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.symbol} {self.amount} @ ${self.avg_buy_price}"

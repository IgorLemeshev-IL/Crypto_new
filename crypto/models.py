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

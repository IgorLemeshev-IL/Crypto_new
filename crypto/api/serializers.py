from decimal import Decimal

from rest_framework import serializers

from crypto.models import Balance, CoinPrice, PortfolioPosition, Snapshot, WatchlistItem


class CoinPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinPrice
        fields = ["id", "name", "symbol", "price", "change_24h"]


class SnapshotSerializer(serializers.ModelSerializer):
    prices = CoinPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Snapshot
        fields = ["id", "created_at", "prices"]


class WatchlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = ["id", "symbol", "created_at"]
        read_only_fields = ["id", "created_at"]


class BalanceSerializer(serializers.ModelSerializer):
    """Сериализатор для баланса пользователя."""

    class Meta:
        model = Balance
        fields = ["amount", "updated_at"]
        read_only_fields = ["updated_at"]


class PortfolioPositionSerializer(serializers.ModelSerializer):
    """Сериализатор для позиции портфеля."""

    current_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    current_value = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    profit = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    profit_percent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PortfolioPosition
        fields = [
            "symbol",
            "amount",
            "avg_buy_price",
            "current_price",
            "current_value",
            "profit",
            "profit_percent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class BuySellSerializer(serializers.Serializer):
    """Сериализатор для покупки/продажи."""

    symbol = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=20, decimal_places=8, min_value=Decimal("0.00000001"))
    price_per_coin = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
        help_text="Опционально. Если не указана — берётся из последнего снимка",
    )

    def validate_symbol(self, value):
        return value.upper()


class PortfolioSummarySerializer(serializers.Serializer):
    """Сериализатор для сводки по портфелю."""

    total_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_invested = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=20, decimal_places=2)
    positions = PortfolioPositionSerializer(many=True)

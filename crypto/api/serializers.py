from rest_framework import serializers

from crypto.models import CoinPrice, Snapshot, WatchlistItem


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

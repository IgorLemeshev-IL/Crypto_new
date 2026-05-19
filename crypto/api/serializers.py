from rest_framework import serializers
from crypto.models import Snapshot, CoinPrice


class CoinPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinPrice
        fields = ['id', 'name', 'symbol', 'price', 'change_24h']


class SnapshotSerializer(serializers.ModelSerializer):
    prices = CoinPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Snapshot
        fields = ['id', 'created_at', 'prices']
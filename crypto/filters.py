from django_filters import rest_framework as filters

from crypto.models import CoinPrice


class CoinPriceFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    symbol = filters.CharFilter(field_name="symbol", lookup_expr="iexact")

    class Meta:
        model = CoinPrice
        fields = ["symbol", "min_price", "max_price"]

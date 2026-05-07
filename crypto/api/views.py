from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter
from crypto.models import Snapshot, CoinPrice
from .serializers import SnapshotSerializer, CoinPriceSerializer


class SnapshotViewSet(ReadOnlyModelViewSet):
    queryset = Snapshot.objects.prefetch_related('prices').all() # загружаем все цены для снимков 1 запросома не для каждого запрос 
    serializer_class = SnapshotSerializer


class CoinPriceViewSet(ReadOnlyModelViewSet):
    queryset = CoinPrice.objects.all()
    serializer_class = CoinPriceSerializer
    filter_backends = [SearchFilter]
    search_fields = ['symbol']
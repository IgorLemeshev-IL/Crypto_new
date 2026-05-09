from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter
from crypto.models import Snapshot, CoinPrice
from .serializers import SnapshotSerializer, CoinPriceSerializer
from rest_framework import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from crypto.services import WatchlistService
from .serializers import WatchlistItemSerializer


class SnapshotViewSet(ReadOnlyModelViewSet):
    queryset = Snapshot.objects.prefetch_related('prices').all() # загружаем все цены для снимков 1 запросома не для каждого запрос 
    serializer_class = SnapshotSerializer


class CoinPriceViewSet(ReadOnlyModelViewSet):
    queryset = CoinPrice.objects.all()
    serializer_class = CoinPriceSerializer
    filter_backends = [SearchFilter]
    filterset_fields = ['symbol']
    search_fields = ['name']


class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = WatchlistService(request.user)
        items = service.list_items()
        serializer = WatchlistItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        symbol = request.data.get('symbol', '')
        service = WatchlistService(request.user)
        try:
            item = service.add_item(symbol)
            serializer = WatchlistItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WatchlistDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, symbol):
        service = WatchlistService(request.user)
        try:
            service.remove_item(symbol)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SnapshotViewSet, CoinPriceViewSet, WatchlistView, WatchlistDeleteView

router = DefaultRouter()
router.register(r'snapshots', SnapshotViewSet)
router.register(r'coins', CoinPriceViewSet)

urlpatterns = [
    path('watchlist/', WatchlistView.as_view(), name='watchlist'),
    path('watchlist/<str:symbol>/', WatchlistDeleteView.as_view(), name='watchlist-delete'),
] + router.urls
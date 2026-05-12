from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    SnapshotViewSet, CoinPriceViewSet,
    WatchlistView, WatchlistDeleteView,
    MarketStatsView, TopMoversView, VolumeLeadersView, CoinsFilterView,
)

router = DefaultRouter()
router.register(r'snapshots', SnapshotViewSet)
router.register(r'coins', CoinPriceViewSet)

urlpatterns = [
    path('watchlist/', WatchlistView.as_view(), name='watchlist'),
    path('watchlist/<str:symbol>/', WatchlistDeleteView.as_view(), name='watchlist-delete'),
    path('analytics/market-stats/', MarketStatsView.as_view(), name='market-stats'),
    path('analytics/top-movers/', TopMoversView.as_view(), name='top-movers'),
    path('analytics/volume-leaders/', VolumeLeadersView.as_view(), name='volume-leaders'),
    path('coins/filter/', CoinsFilterView.as_view(), name='coins-filter'),
] + router.urls
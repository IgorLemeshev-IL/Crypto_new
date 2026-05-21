from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    # Основные views
    CoinPriceViewSet,
    CoinsFilterView,
    FetchSnapshotView,
    MarketStatsView,
    PortfolioBuyView,
    # Портфельные views
    PortfolioListView,
    PortfolioSellView,
    PortfolioSummaryView,
    SnapshotViewSet,
    TaskStatusView,
    TopMoversView,
    VolumeLeadersView,
    WatchlistDeleteView,
    WatchlistView,
)

router = DefaultRouter()
router.register(r"snapshots", SnapshotViewSet)
router.register(r"coins", CoinPriceViewSet)

urlpatterns = [
    # Watchlist
    path("watchlist/", WatchlistView.as_view(), name="watchlist"),
    path("watchlist/<str:symbol>/", WatchlistDeleteView.as_view(), name="watchlist-delete"),
    # Analytics
    path("analytics/market-stats/", MarketStatsView.as_view(), name="market-stats"),
    path("analytics/top-movers/", TopMoversView.as_view(), name="top-movers"),
    path("analytics/volume-leaders/", VolumeLeadersView.as_view(), name="volume-leaders"),
    # Coins
    path("coins/filter/", CoinsFilterView.as_view(), name="coins-filter"),
    # Tasks
    path("tasks/fetch-snapshot/", FetchSnapshotView.as_view(), name="fetch-snapshot"),
    path("tasks/<str:task_id>/", TaskStatusView.as_view(), name="task-status"),
    # Portfolio
    path("portfolio/", PortfolioListView.as_view(), name="portfolio-list"),
    path("portfolio/buy/", PortfolioBuyView.as_view(), name="portfolio-buy"),
    path("portfolio/sell/", PortfolioSellView.as_view(), name="portfolio-sell"),
    path("portfolio/summary/", PortfolioSummaryView.as_view(), name="portfolio-summary"),
] + router.urls

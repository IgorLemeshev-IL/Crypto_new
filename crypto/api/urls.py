from rest_framework.routers import DefaultRouter
from .views import SnapshotViewSet, CoinPriceViewSet


router = DefaultRouter() # ---> атоматом создаю urls для ViewSet
router.register(r'Snapshots', SnapshotViewSet, basename='snapshot') # /api/snapshots/ # /api/snapshots/{id}
router.register(r'Coins', CoinPriceViewSet, basename='coin')

urlpatterns = router.urls
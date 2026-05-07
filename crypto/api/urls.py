from rest_framework.routers import DefaultRouter
from .views import SnapshotViewSet, CoinPriceViewSet


router = DefaultRouter() # ---> атоматом создаю urls для ViewSet
router.register(r'snapshots', SnapshotViewSet) # /api/snapshots/ # /api/snapshots/{id}
router.register(r'coins', CoinPriceViewSet) # /api/coins/

urlpatterns = router.urls 
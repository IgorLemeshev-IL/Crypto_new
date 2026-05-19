import pytest
from django.contrib.auth.models import User
from unittest.mock import patch
from django.test.utils import CaptureQueriesContext
from django.db import connection


@pytest.mark.django_db
class TestWatchlistAPI:
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='pass')
    
    @pytest.fixture
    def auth_client(self, client, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {refresh.access_token}'
        return client
    
    def test_get_empty_watchlist(self, auth_client):
        response = auth_client.get('/api/watchlist/')
        assert response.status_code == 200
        assert response.json() == []
    
    def test_add_to_watchlist(self, auth_client):
        # Мокаем валидацию чтобы не ходить в API
        with patch('crypto.services.WatchlistService._validate_symbol'):
            response = auth_client.post('/api/watchlist/', {'symbol': 'BTC'}, format='json')
        assert response.status_code == 201
        assert response.json()['symbol'] == 'BTC'
    
    def test_delete_from_watchlist(self, auth_client):
        with patch('crypto.services.WatchlistService._validate_symbol'):
            auth_client.post('/api/watchlist/', {'symbol': 'BTC'}, format='json')
        response = auth_client.delete('/api/watchlist/BTC/')
        assert response.status_code == 204
    
    def test_unauthorized_access(self, client):
        response = client.get('/api/watchlist/')
        assert response.status_code == 401
    
    def test_isolation_between_users(self, auth_client, user):
        other_user = User.objects.create_user(username='other', password='pass')
        from crypto.services import WatchlistService
        
        with patch.object(WatchlistService, '_validate_symbol'):
            WatchlistService(other_user).add_item('ETH')
        
        response = auth_client.get('/api/watchlist/')
        assert len(response.json()) == 0  # testuser не видит ETH от other

    def test_snapshots_query_count(self, client):
        """Проверяем prefetch_related (не более 4 запросов)."""
        from crypto.models import Snapshot, CoinPrice
        s = Snapshot.objects.create()
        CoinPrice.objects.create(snapshot=s, name='BTC', symbol='btc', price=50000, change_24h=2.5)
        CoinPrice.objects.create(snapshot=s, name='ETH', symbol='eth', price=3000, change_24h=-1.2)
    
        with CaptureQueriesContext(connection) as queries:
            response = client.get('/api/snapshots/')
            assert response.status_code == 200
    
        assert len(queries) <= 4  # prefetch должен уложиться в 4 запроса
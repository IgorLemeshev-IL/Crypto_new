import pytest
from django.contrib.auth.models import User
from unittest.mock import patch

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
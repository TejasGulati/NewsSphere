import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import BlacklistedToken

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(email, password, name):
        user = User.objects.create_user(email=email, password=password, name=name)
        return user
    return _create_user

@pytest.mark.django_db
def test_register_view(api_client):
    url = reverse('register')
    data = {'email': 'testuser@example.com', 'password': 'password123', 'name': 'Test User'}
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['email'] == 'testuser@example.com'
    assert 'password' not in response.data  # Ensure password is not returned in response

@pytest.mark.django_db
def test_login_view(api_client, create_user):
    user = create_user(email='testuser@example.com', password='password123', name='Test User')
    url = reverse('login')
    data = {'email': 'testuser@example.com', 'password': 'password123'}
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert 'jwt' in response.cookies  # Check if JWT cookie is set

@pytest.mark.django_db
def test_refresh_token_view(api_client, create_user):
    user = create_user(email='testuser@example.com', password='password123', name='Test User')
    refresh = RefreshToken.for_user(user)
    api_client.cookies['jwt'] = str(refresh)  # Ensure token is a string
    url = reverse('refresh')
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

@pytest.mark.django_db
def test_user_view(api_client, create_user):
    user = create_user(email='testuser@example.com', password='password123', name='Test User')
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    url = reverse('user')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'testuser@example.com'

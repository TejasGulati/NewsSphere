import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError
from users.models import BlacklistedToken

User = get_user_model()

@pytest.fixture
def create_user():
    """Fixture to create a user for testing."""
    def _create_user(email, password=None, **extra_fields):
        return User.objects.create_user(email=email, password=password, **extra_fields)
    return _create_user

@pytest.fixture
def create_superuser():
    """Fixture to create a superuser for testing."""
    def _create_superuser(email, password=None, **extra_fields):
        return User.objects.create_superuser(email=email, password=password, **extra_fields)
    return _create_superuser

@pytest.mark.django_db
def test_create_user(create_user):
    user = create_user(email='testuser@example.com', password='password123', name='Test User')
    assert user.email == 'testuser@example.com'
    assert user.check_password('password123')
    assert user.name == 'Test User'
    assert not user.is_staff
    assert not user.is_superuser

@pytest.mark.django_db
def test_create_superuser(create_superuser):
    superuser = create_superuser(email='superuser@example.com', password='password123', name='Super User')
    assert superuser.email == 'superuser@example.com'
    assert superuser.check_password('password123')
    assert superuser.name == 'Super User'
    assert superuser.is_staff
    assert superuser.is_superuser

@pytest.mark.django_db
def test_user_str_method(create_user):
    user = create_user(email='testuser@example.com', password='password123', name='Test User')
    assert str(user) == 'testuser@example.com'

@pytest.mark.django_db
def test_user_email_unique(create_user):
    email = 'unique@example.com'
    create_user(email=email, password='password123', name='Unique User')
    with pytest.raises(IntegrityError):
        create_user(email=email, password='password123', name='Another User')

@pytest.mark.django_db
def test_user_email_normalize(create_user):
    email = 'TEST@ExAmPle.CoM'
    user = create_user(email=email, password='password123', name='Test User')
    assert user.email == 'TEST@example.com'

@pytest.mark.django_db
def test_user_required_fields():
    assert User.REQUIRED_FIELDS == ['name']
    assert User.USERNAME_FIELD == 'email'

@pytest.mark.django_db
def test_blacklisted_token_model(create_user):
    user = create_user(email='testuser@example.com', password='password123', name='Test User')
    token = BlacklistedToken.objects.create(token='dummy_token', user=user)
    assert token.token == 'dummy_token'
    assert token.user == user
    assert isinstance(token.created_at, timezone.datetime)

@pytest.mark.django_db
def test_blacklisted_token_str_method(create_user):
    user = create_user(email='testuser@example.com', password='password123', name='Test User')
    token = BlacklistedToken.objects.create(token='dummy_token', user=user)
    assert str(token) == f"Blacklisted token for testuser@example.com"

@pytest.mark.django_db
def test_blacklisted_token_user_cascade(create_user):
    user = create_user(email='testuser@example.com', password='password123', name='Test User')
    BlacklistedToken.objects.create(token='dummy_token', user=user)
    assert BlacklistedToken.objects.count() == 1
    user.delete()
    assert BlacklistedToken.objects.count() == 0
import pytest
from django.contrib.auth import get_user_model
from dashboard.models import Article, Bookmark, UserArticleView

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(email='testuser@example.com', password='password123')

@pytest.fixture
def article():
    return Article.objects.create(
        title='Sample Article',
        content='This is a sample article content.',
        author='John Doe',
        source_url='http://example.com/article',
        category='technology'
    )

@pytest.fixture
def bookmark(user, article):
    return Bookmark.objects.create(user=user, article=article)

@pytest.fixture
def user_article_view(user, article):
    return UserArticleView.objects.create(user=user, article=article)

@pytest.mark.django_db
def test_article_creation(article):
    assert article.title == 'Sample Article'
    assert article.content == 'This is a sample article content.'
    assert article.author == 'John Doe'
    assert article.source_url == 'http://example.com/article'
    assert article.category == 'technology'
    assert article.created_at is not None
    assert article.updated_at is not None

@pytest.mark.django_db
def test_bookmark_creation(bookmark):
    assert Bookmark.objects.count() == 1
    assert bookmark.user.email == 'testuser@example.com'
    assert bookmark.article.title == 'Sample Article'
    assert bookmark.created_at is not None

@pytest.mark.django_db
def test_user_article_view_creation(user_article_view):
    assert UserArticleView.objects.count() == 1
    assert user_article_view.user.email == 'testuser@example.com'
    assert user_article_view.article.title == 'Sample Article'
    assert user_article_view.viewed_at is not None

@pytest.mark.django_db
def test_article_str_method(article):
    assert str(article) == 'Sample Article'

@pytest.mark.django_db
def test_bookmark_str_method(bookmark):
    assert str(bookmark) == 'testuser@example.com bookmarked Sample Article'

@pytest.mark.django_db
def test_user_article_view_str_method(user_article_view):
    assert str(user_article_view) == 'testuser@example.com viewed Sample Article'

@pytest.mark.django_db
def test_article_category_choices():
    article = Article.objects.create(
        title='Another Article',
        content='Content of another article.',
        source_url='http://example.com/another-article',
        category='sports'
    )
    assert article.category == 'sports'

@pytest.mark.django_db
def test_article_source_url_unique():
    Article.objects.create(
        title='Article with Unique URL',
        content='Content.',
        source_url='http://example.com/unique-url',
        category='science'
    )
    with pytest.raises(Exception):
        Article.objects.create(
            title='Article with Duplicate URL',
            content='Content.',
            source_url='http://example.com/unique-url',
            category='science'
        )

# import pytest
# from rest_framework.test import APIClient
# from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from rest_framework import status
# from dashboard.models import Article, Bookmark

# @pytest.fixture
# def api_client():
#     return APIClient()

# @pytest.fixture
# def user(api_client):
#     User = get_user_model()
#     user = User.objects.create_user(email='testuser@example.com', password='password')
#     access_token = AccessToken.for_user(user)
#     api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
#     return api_client, user

# @pytest.mark.django_db
# class TestArticlesView:
#     def test_get_articles(self, user):
#         client, _ = user
#         Article.objects.create(
#             title='Sample Article 1',
#             content='This is a sample article content.',
#             source_url='http://example.com/article1',
#             media_url='http://example.com/media1.jpg',
#             category='technology'
#         )
#         Article.objects.create(
#             title='Sample Article 2',
#             content='Another sample article content.',
#             source_url='http://example.com/article2',
#             media_url='http://example.com/media2.jpg',
#             category='sports'
#         )
#         response = client.get(reverse('articles'))
#         assert response.status_code == status.HTTP_200_OK
#         assert len(response.data) > 0
#         assert response.data[0]['title'] in ['Sample Article 1', 'Sample Article 2']

#     def test_get_article_by_id(self, user):
#         client, _ = user
#         article = Article.objects.create(
#             title='Sample Article',
#             content='This is a sample article content.',
#             source_url='http://example.com/article',
#             media_url='http://example.com/media.jpg',
#             category='technology'
#         )
#         response = client.get(reverse('article-detail', args=[article.id]))
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data['title'] == 'Sample Article'

# @pytest.mark.django_db
# class TestBookmarksView:
#     def test_post_bookmark(self, user):
#         client, user_obj = user
#         article = Article.objects.create(
#             title='Sample Article',
#             content='This is a sample article content.',
#             source_url='http://example.com/article',
#             media_url='http://example.com/media.jpg',
#             category='technology'
#         )
#         response = client.post(reverse('bookmarks'), {'article_id': article.id})
#         assert response.status_code == status.HTTP_201_CREATED
#         assert response.data['article_id'] == article.id

#     def test_delete_bookmark(self, user):
#         client, user_obj = user
#         article = Article.objects.create(
#             title='Sample Article',
#             content='This is a sample article content.',
#             source_url='http://example.com/article',
#             media_url='http://example.com/media.jpg',
#             category='technology'
#         )
#         bookmark = Bookmark.objects.create(user=user_obj, article=article)
#         # Use URL pattern for deleting a bookmark
#         response = client.delete(reverse('bookmark-detail', args=[article.id]))
#         assert response.status_code == status.HTTP_204_NO_CONTENT
#         assert not Bookmark.objects.filter(user=user_obj, article=article).exists()

# @pytest.mark.django_db
# class TestDashboardView:
#     def test_get_dashboard(self, user):
#         client, _ = user
#         response = client.get(reverse('dashboard'))
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data['message'] == 'Welcome to your dashboard!'
#         assert response.data['user']['email'] == 'testuser@example.com'


# # @pytest.mark.django_db
# # class TestNotificationsView:
# #     def test_get_notifications(self, user):
# #         client, _ = user
# #         response = client.get(reverse('notifications'))
# #         assert response.status_code == status.HTTP_200_OK
# #         assert response.data['message'] == 'Notifications list'

# # @pytest.mark.django_db
# # class TestCommentsView:
# #     def test_get_comments(self, user):
# #         client, _ = user
# #         response = client.get(reverse('comments'))
# #         assert response.status_code == status.HTTP_200_OK
# #         assert response.data['message'] == 'Comments list'

# @pytest.mark.django_db
# class TestLogoutView:
#     def test_post_logout(self, user):
#         client, _ = user
#         response = client.post(reverse('logout'))
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data['message'] == 'Successfully logged out'

# @pytest.mark.django_db
# class TestRecommendedArticlesView:
#     def test_get_recommended_articles(self, user):
#         client, _ = user
#         Article.objects.create(
#             title='Recommended Article 1',
#             content='Content for recommended article.',
#             source_url='http://example.com/recommended1',
#             category='technology'
#         )
#         Article.objects.create(
#             title='Recommended Article 2',
#             content='Content for recommended article.',
#             source_url='http://example.com/recommended2',
#             category='technology'
#         )
#         response = client.get(reverse('recommended-articles'))
#         assert response.status_code == status.HTTP_200_OK
#         assert isinstance(response.data, list)

# @pytest.mark.django_db
# class TestTrendingArticlesView:
#     def test_get_trending_articles(self, user):
#         client, _ = user
#         Article.objects.create(
#             title='Trending Article 1',
#             content='Content for trending article.',
#             source_url='http://example.com/trending1',
#             category='technology'
#         )
#         Article.objects.create(
#             title='Trending Article 2',
#             content='Content for trending article.',
#             source_url='http://example.com/trending2',
#             category='technology'
#         )
#         response = client.get(reverse('trending-articles'))
#         assert response.status_code == status.HTTP_200_OK
#         assert isinstance(response.data, list)


import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from dashboard.models import Article, Bookmark

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(api_client):
    User = get_user_model()
    user = User.objects.create_user(email='testuser@example.com', password='password')
    access_token = AccessToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client, user

@pytest.mark.django_db
class TestArticlesView:
    def test_get_articles(self, user):
        client, _ = user
        Article.objects.create(
            title='Sample Article 1',
            content='This is a sample article content.',
            source_url='http://example.com/article1',
            media_url='http://example.com/media1.jpg',
            category='technology'
        )
        Article.objects.create(
            title='Sample Article 2',
            content='Another sample article content.',
            source_url='http://example.com/article2',
            media_url='http://example.com/media2.jpg',
            category='sports'
        )
        response = client.get(reverse('articles'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        assert any(article['title'] in ['Sample Article 1', 'Sample Article 2'] for article in response.data['results'])

    def test_get_article_by_id(self, user):
        client, _ = user
        article = Article.objects.create(
            title='Sample Article',
            content='This is a sample article content.',
            source_url='http://example.com/article',
            media_url='http://example.com/media.jpg',
            category='technology'
        )
        response = client.get(reverse('article-detail', args=[article.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Sample Article'

@pytest.mark.django_db
class TestBookmarksView:
    def test_post_bookmark(self, user):
        client, user_obj = user
        article = Article.objects.create(
            title='Sample Article',
            content='This is a sample article content.',
            source_url='http://example.com/article',
            media_url='http://example.com/media.jpg',
            category='technology'
        )
        response = client.post(reverse('bookmarks'), {'article_id': article.id})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['bookmark']['article_id'] == article.id

    def test_delete_bookmark(self, user):
        client, user_obj = user
        article = Article.objects.create(
            title='Sample Article',
            content='This is a sample article content.',
            source_url='http://example.com/article',
            media_url='http://example.com/media.jpg',
            category='technology'
        )
        bookmark = Bookmark.objects.create(user=user_obj, article=article)
        response = client.delete(reverse('bookmark-detail', args=[article.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Bookmark.objects.filter(user=user_obj, article=article).exists()

@pytest.mark.django_db
class TestDashboardView:
    def test_get_dashboard(self, user):
        client, _ = user
        response = client.get(reverse('dashboard'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Welcome to your dashboard!'
        assert response.data['user']['email'] == 'testuser@example.com'

@pytest.mark.django_db
class TestLogoutView:
    def test_post_logout(self, user):
        client, _ = user
        response = client.post(reverse('logout'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Successfully logged out'

@pytest.mark.django_db
class TestRecommendedArticlesView:
    def test_get_recommended_articles(self, user):
        client, _ = user
        Article.objects.create(
            title='Recommended Article 1',
            content='Content for recommended article.',
            source_url='http://example.com/recommended1',
            category='technology'
        )
        Article.objects.create(
            title='Recommended Article 2',
            content='Content for recommended article.',
            source_url='http://example.com/recommended2',
            category='technology'
        )
        response = client.get(reverse('recommended-articles'))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

@pytest.mark.django_db
class TestTrendingArticlesView:
    def test_get_trending_articles(self, user):
        client, _ = user
        Article.objects.create(
            title='Trending Article 1',
            content='Content for trending article.',
            source_url='http://example.com/trending1',
            category='technology'
        )
        Article.objects.create(
            title='Trending Article 2',
            content='Content for trending article.',
            source_url='http://example.com/trending2',
            category='technology'
        )
        response = client.get(reverse('trending-articles'))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

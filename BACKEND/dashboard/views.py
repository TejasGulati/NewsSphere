from datetime import timedelta
from tokenize import TokenError
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import logout as django_logout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from dashboard.models import Article, Bookmark, UserArticleView
from dashboard.serializers import ArticleSerializer, BookmarkSerializer
from users.serializers import UserSerializer
from django.shortcuts import get_object_or_404
import logging
import random
from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger(__name__)

class DashboardView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user)
        return Response({'message': 'Welcome to your dashboard!', 'user': serializer.data})


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArticlesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, article_id=None):
        if article_id is not None:
            return self.retrieve_article(request, article_id)
        else:
            return self.list_articles(request)

    def retrieve_article(self, request, article_id):
        # Fetch a specific article by ID
        article = get_object_or_404(Article, id=article_id)

        # Check if the article has a valid media_url
        if not article.media_url:
            return Response({"error": "Article has no valid media URL"}, status=status.HTTP_404_NOT_FOUND)

        # Log the article view
        UserArticleView.objects.create(user=request.user, article=article)

        serializer = ArticleSerializer(article, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list_articles(self, request):
        # Get the category from the query parameters
        category = request.query_params.get('category')

        # Fetch all articles or filter by category if provided
        queryset = Article.objects.filter(category=category) if category else Article.objects.all()

        # Filter articles based on content relevance
        filtered_articles = [
            article for article in queryset
            if article.content.strip() != 'No summary available' and
            len(article.title.split()) > 2 and
            article.media_url and
            self.is_content_relevant(article)
        ]

        # Sort articles by creation date (newest first)
        filtered_articles.sort(key=lambda x: x.created_at, reverse=True)

        # Paginate the results
        paginator = self.pagination_class()
        paginated_articles = paginator.paginate_queryset(filtered_articles, request)

        # Serialize and return paginated articles
        serializer = ArticleSerializer(paginated_articles, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    def is_content_relevant(self, article):
        # Example relevance check: content should include keywords from the title
        title_keywords = set(article.title.lower().split())
        content_keywords = set(article.content.lower().split())
        return any(keyword in content_keywords for keyword in title_keywords)

class UserArticleViewCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        view_count = UserArticleView.objects.filter(user=request.user).count()
        return Response({'view_count': view_count}, status=status.HTTP_200_OK)
class BookmarksView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve all bookmarks for the authenticated user
        bookmarks = Bookmark.objects.filter(user=request.user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Add a new bookmark
        article_id = request.data.get('article_id')
        if not article_id:
            return Response({'error': 'Article ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

        bookmark, created = Bookmark.objects.get_or_create(user=request.user, article=article)
        if not created:
            return Response({'message': 'Article already bookmarked'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookmarkSerializer(bookmark)

        # Remove the 'article' field from the serialized data
        bookmark_data = serializer.data
        if 'article' in bookmark_data:
            del bookmark_data['article']

        response_data = {
            'message': 'Bookmark saved successfully',
            'bookmark': bookmark_data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request, article_id=None):
        # Remove a bookmark
        if article_id is None:
            return Response({'error': 'Article ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

        bookmark = Bookmark.objects.filter(user=request.user, article=article).first()
        if bookmark:
            bookmark.delete()
            return Response({'message': 'Bookmark removed'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Bookmark not found'}, status=status.HTTP_404_NOT_FOUND)


class BookmarkCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Count all bookmarks for the authenticated user
        bookmark_count = Bookmark.objects.filter(user=request.user).count()
        return Response({'bookmark_count': bookmark_count}, status=status.HTTP_200_OK)

class NotificationsView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response({'message': 'Notifications list'})

class CommentsView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response({'message': 'Comments list'})

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        django_logout(request)

        auth_header = request.headers.get('Authorization', None)
        if auth_header:
            try:
                token_type, token = auth_header.split(' ')
                if token_type.lower() != 'bearer':
                    return Response({"error": "Invalid token type"}, status=status.HTTP_400_BAD_REQUEST)

                access_token = AccessToken(token)
                # Implement token blacklisting or invalidation if needed
                # Example: access_token.blacklist()

            except TokenError as e:
                return Response({"error": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Token required"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

class RecommendedArticlesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Count the user's bookmarks and article views
        bookmark_count = Bookmark.objects.filter(user=user).count()
        article_view_count = UserArticleView.objects.filter(user=user).count()

        if bookmark_count > 5 and article_view_count > 20:
            # Example logic for recommendations when criteria are met
            recent_views = UserArticleView.objects.filter(user=user).order_by('-viewed_at')[:5]
            viewed_articles = [view.article for view in recent_views]

            # Find articles that are not in the recently viewed list
            recommended_articles = Article.objects.exclude(id__in=[article.id for article in viewed_articles])

            # Filter articles based on content relevance
            filtered_articles = [
                article for article in recommended_articles
                if self.is_content_relevant(article)
            ]

            # Limit to top 3 articles
            top_recommended_articles = filtered_articles[:3]
        else:
            # Show 3 random articles if criteria are not met
            all_articles = Article.objects.all()
            filtered_articles = [
                article for article in all_articles
                if self.is_content_relevant(article)
            ]
            top_recommended_articles = random.sample(filtered_articles, min(3, len(filtered_articles)))

        serializer = ArticleSerializer(top_recommended_articles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def is_content_relevant(self, article):
        # Example relevance check: content should include keywords from the title
        title_keywords = set(article.title.lower().split())
        content_keywords = set(article.content.lower().split())
        return any(keyword in content_keywords for keyword in title_keywords)

class TrendingArticlesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Count the user's bookmarks and article views
        bookmark_count = Bookmark.objects.filter(user=user).count()
        article_view_count = UserArticleView.objects.filter(user=user).count()

        if bookmark_count > 5 and article_view_count > 20:
            # Trending articles based on view count in the last 30 days
            thirty_days_ago = timezone.now() - timedelta(days=30)
            trending_articles = Article.objects.filter(
                userarticleview__viewed_at__gte=thirty_days_ago
            ).annotate(view_count=Count('userarticleview')).order_by('-view_count')[:5]
        else:
            # Show 5 random articles if criteria are not met
            all_articles = Article.objects.all()
            filtered_articles = [
                article for article in all_articles
                if self.is_content_relevant(article)
            ]
            trending_articles = random.sample(filtered_articles, min(3, len(filtered_articles)))

        serializer = ArticleSerializer(trending_articles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def is_content_relevant(self, article):
        # Example relevance check: content should include keywords from the title
        title_keywords = set(article.title.lower().split())
        content_keywords = set(article.content.lower().split())
        return any(keyword in content_keywords for keyword in title_keywords)

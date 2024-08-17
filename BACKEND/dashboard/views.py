from datetime import timedelta
from tokenize import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import logout as django_logout
from rest_framework import status
from django.db.models import Count
from dashboard.models import Article, Bookmark, Notification, UserArticleView
from dashboard.serializers import ArticleSerializer, BookmarkSerializer, NotificationSerializer
from users.serializers import UserSerializer
from django.shortcuts import get_object_or_404
import logging
import random
from rest_framework.pagination import PageNumberPagination
import requests
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from dotenv import load_dotenv
import os

from users.models import User 


# Load the .env file
load_dotenv()
logger = logging.getLogger(__name__)


class DashboardView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check and create a welcome notification if this is the first login
        if not user.last_login:
            create_notification(user, "Welcome back! It's great to see you again.")
            user.last_login = timezone.now()  # Update last_login time
            user.save()  # Save user with the updated last_login

        serializer = UserSerializer(user)
        return Response({'message': 'Welcome to your dashboard!', 'user': serializer.data})



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100

import re
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from better_profanity import profanity
from .models import Article, UserArticleView, Bookmark
from .serializers import ArticleSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

profanity.load_censor_words()

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
            if self.is_content_relevant(article)
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
        # Check if the content is at least 50 characters long
        if len(article.content.strip()) < 250:
            return False

        # Remove HTML entities and special characters
        cleaned_content = re.sub(r'&[a-zA-Z0-9#]+;', '', article.content)  # Remove HTML entities
        cleaned_content = re.sub(r'[^\w\s]', '', cleaned_content)  # Remove special characters

        # Example relevance check: content should include keywords from the title
        title_keywords = set(article.title.lower().split())
        content_keywords = set(cleaned_content.lower().split())
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
        bookmarks = Bookmark.objects.filter(user=request.user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        article_id = request.data.get('article_id')
        if not article_id:
            return Response({'error': 'Article ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

        bookmark, created = Bookmark.objects.get_or_create(user=request.user, article=article)
        if created:
            create_notification(request.user, f"You bookmarked the article: {article.title}")
        else:
            return Response({'message': 'Article already bookmarked'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookmarkSerializer(bookmark)
        bookmark_data = serializer.data
        if 'article' in bookmark_data:
            del bookmark_data['article']

        response_data = {
            'message': 'Bookmark saved successfully',
            'bookmark': bookmark_data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request, article_id=None):
        if article_id is None:
            return Response({'error': 'Article ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

        bookmark = Bookmark.objects.filter(user=request.user, article=article).first()
        if bookmark:
            bookmark.delete()
            create_notification(request.user, f"You removed the bookmark for: {article.title}")
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
    # Check if the content is at least 50 characters long
        if len(article.content.strip()) < 250:
            return False

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
    # Check if the content is at least 50 characters long
        if len(article.content.strip()) < 250 :
            return False

    # Example relevance check: content should include keywords from the title
        title_keywords = set(article.title.lower().split())
        content_keywords = set(article.content.lower().split())
        return any(keyword in content_keywords for keyword in title_keywords)


class WeatherView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        api_key = os.getenv("WEATHER_API_KEY")
        current_base_url = "http://api.openweathermap.org/data/2.5/weather"
        forecast_base_url = "http://api.openweathermap.org/data/2.5/forecast"
        air_pollution_base_url = "http://api.openweathermap.org/data/2.5/air_pollution"

        # Check if latitude and longitude are provided
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        city = request.query_params.get('city')

        # Determine request parameters
        if lat and lon:
            current_params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric'
            }
            forecast_params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric'
            }
            air_pollution_params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key
            }
        elif city:
            # Fetch coordinates for the city
            geocode_params = {
                'q': city,
                'appid': api_key,
                'units': 'metric'
            }
            geocode_response = requests.get(current_base_url, params=geocode_params)
            geocode_data = geocode_response.json()

            if geocode_response.status_code != 200 or "coord" not in geocode_data:
                return Response({"error": "Failed to geocode city name or city not found"},
                                status=geocode_response.status_code)

            lat = geocode_data["coord"]["lat"]
            lon = geocode_data["coord"]["lon"]

            # Use the obtained coordinates for other requests
            current_params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric'
            }
            forecast_params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric'
            }
            air_pollution_params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key
            }
        else:
            current_params = {
                'q': 'New Delhi',  # Default city
                'appid': api_key,
                'units': 'metric'
            }
            forecast_params = {
                'q': 'New Delhi',
                'appid': api_key,
                'units': 'metric'
            }
            air_pollution_params = {
                'lat': 28.6139,  # Approximate latitude for New Delhi
                'lon': 77.2090,  # Approximate longitude for New Delhi
                'appid': api_key
            }

        try:
            # Fetch current weather data
            current_response = requests.get(current_base_url, params=current_params)
            current_data = current_response.json()

            if current_response.status_code != 200:
                return Response({"error": current_data.get("message", "Failed to fetch current weather data")},
                                status=current_response.status_code)

            # Fetch 5-day forecast data
            forecast_response = requests.get(forecast_base_url, params=forecast_params)
            forecast_data = forecast_response.json()

            if forecast_response.status_code != 200:
                return Response({"error": forecast_data.get("message", "Failed to fetch forecast data")},
                                status=forecast_response.status_code)

            # Fetch air pollution data
            air_pollution_response = requests.get(air_pollution_base_url, params=air_pollution_params)
            air_pollution_data = air_pollution_response.json()

            if air_pollution_response.status_code != 200:
                return Response({"error": air_pollution_data.get("message", "Failed to fetch air pollution data")},
                                status=air_pollution_response.status_code)

            # Extract relevant forecast data
            forecast_list = forecast_data["list"]
            filtered_forecast = []
            for entry in forecast_list[::8][:5]:  # Taking 1 entry per day (8 hours interval) for 5 days
                filtered_forecast.append({
                    "date": entry["dt_txt"],
                    "temperature": entry["main"]["temp"],
                    "description": entry["weather"][0]["description"]
                })

            # Combine current weather, forecast, and air pollution data
            weather_info = {
                "current": {
                    "city": current_data["name"],
                    "temperature": current_data["main"]["temp"],
                    "description": current_data["weather"][0]["description"],
                    "humidity": current_data["main"]["humidity"],
                    "wind_speed": current_data["wind"]["speed"],
                },
                "forecast": {
                    "city": forecast_data["city"]["name"],
                    "forecast_data": filtered_forecast
                },
                "air_pollution": {
                    "aqi": air_pollution_data["list"][0]["main"]["aqi"],
                    "components": air_pollution_data["list"][0]["components"]
                }
            }

            return Response(weather_info, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('created_at')
        
        if not notifications.exists():
            return Response({'message': 'No notifications found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Mark notifications as read
        notifications.update(is_read=True)
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, notification_id=None):
        if notification_id is None:
            return Response({'error': 'Notification ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)



def send_read_later_reminders():
    for user in User.objects.all():
        unread_bookmarks = Bookmark.objects.filter(user=user, is_read=False)
        if unread_bookmarks.exists():
            create_notification(user, f"You have {unread_bookmarks.count()} unread bookmarked articles. Don't forget to check them out!")

def notify_article_update(article):
    bookmarked_users = User.objects.filter(bookmarks__article=article)
    for user in bookmarked_users:
        create_notification(user, f"An article you bookmarked has been updated: {article.title}")

def send_weekly_summary():
    for user in User.objects.all():
        article_views = UserArticleView.objects.filter(
            user=user,
            viewed_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        new_bookmarks = Bookmark.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        create_notification(user, f"Your weekly summary: You viewed {article_views} articles and created {new_bookmarks} new bookmarks.")


def create_notification(user, message):
    Notification.objects.create(user=user, message=message, is_read=False)

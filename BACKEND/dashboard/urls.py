from django.urls import path
from dashboard.views import (
    DashboardView, ArticlesView, BookmarksView, 
    NotificationsView, CommentsView, LogoutView, 
    UserArticleViewCountView, BookmarkCountView, 
    RecommendedArticlesView, TrendingArticlesView,WeatherView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('articles/', ArticlesView.as_view(), name='articles'),
    path('articles/<int:article_id>/', ArticlesView.as_view(), name='article-detail'),
    path('articles/category/', ArticlesView.as_view(), name='articles-by-category'),  # Updated path without category in URL
    path('bookmarks/', BookmarksView.as_view(), name='bookmarks'),
    path('bookmarks/<int:article_id>/', BookmarksView.as_view(), name='bookmark-detail'), 
    path('logout/', LogoutView.as_view(), name='logout'),
    path('articles/view-count/', UserArticleViewCountView.as_view(), name='user-article-view-count'),
    path('bookmarks/count/', BookmarkCountView.as_view(), name='bookmark-count'),
    path('articles/recommended/', RecommendedArticlesView.as_view(), name='recommended-articles'),
    path('articles/trending/', TrendingArticlesView.as_view(), name='trending-articles'),
    path('weather/', WeatherView.as_view(), name='weather'),
]

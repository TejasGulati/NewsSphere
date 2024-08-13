from django.urls import path
from users.views import RegisterView, UserView, LoginView, RefreshTokenView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserView.as_view(), name='user'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
]

import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.shortcuts import get_object_or_404
from users.serializers import UserSerializer
from users.models import User, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError
import logging

# Set up logger
logger = logging.getLogger(__name__)

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserSerializer
from users.models import User

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Check if email already exists
                if User.objects.filter(email=serializer.validated_data['email']).exists():
                    return Response({'email': ['Email already exists.']}, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate password
                validate_password(serializer.validated_data['password'])
                
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email:
            return Response({'email': ['Email is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'password': ['Password is required.']}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({'email': ['User not found.']}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({'password': ['Incorrect password.']}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            'access': access_token,
            'refresh': refresh_token
        })
        response.set_cookie(key='jwt', value=refresh_token, httponly=True, secure=True)
        return response
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('jwt')

        if not refresh_token:
            raise AuthenticationFailed("Refresh token is missing!")

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except TokenError:
            raise AuthenticationFailed("Invalid refresh token!")

        return Response({'access': access_token})

class UserView(APIView):
    def get(self, request):
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            raise AuthenticationFailed("Unauthenticated! No authorization header provided.")

        parts = authorization_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthenticationFailed("Invalid token format! Expected format is 'Bearer <token>'.")

        access_token = parts[1]

        # Check if token is blacklisted
        if BlacklistedToken.objects.filter(token=access_token).exists():
            raise AuthenticationFailed("Token is blacklisted!")

        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            if 'user_id' not in payload:
                raise AuthenticationFailed("Token has no user_id field!")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired!")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token! {str(e)}")

        user = get_object_or_404(User, id=payload['user_id'])

        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    
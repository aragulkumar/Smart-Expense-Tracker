from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
import json

def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login endpoint
    Expected JSON: {"username": "demo", "password": "demo123"}
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return Response({
                'success': False,
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Generate JWT tokens
                tokens = get_tokens_for_user(user)
                
                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Account is deactivated'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'success': False,
                'message': 'Invalid username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred during login'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    User registration endpoint
    Expected JSON: {"username": "newuser", "password": "newpass123"}
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        if not username or not password:
            return Response({
                'success': False,
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 6:
            return Response({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create new user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Generate JWT tokens for the new user
            tokens = get_tokens_for_user(user)
            
            return Response({
                'success': True,
                'message': 'Account created successfully',
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError:
            return Response({
                'success': False,
                'message': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred during registration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def logout_view(request):
    """
    User logout endpoint - blacklist the refresh token
    Expected JSON: {"refresh": "refresh_token_here"}
    """
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh')
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({
                    'success': True,
                    'message': 'Successfully logged out'
                }, status=status.HTTP_200_OK)
            except Exception:
                return Response({
                    'success': False,
                    'message': 'Invalid refresh token'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def user_profile_view(request):
    """
    Get current user profile
    Requires Authentication
    """
    if request.user.is_authenticated:
        return Response({
            'success': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'Authentication required'
        }, status=status.HTTP_401_UNAUTHORIZED)
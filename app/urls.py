from django.urls import path
from .views import RegisterView, UserProfileDetailView, UserProfileCreateView,home,DiabeticProfileCreateView,DiabeticProfileDetailView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # View to obtain JWT access and refresh tokens (login)
    TokenRefreshView,     # View to refresh access token using refresh token
    TokenBlacklistView,   # View to blacklist a refresh token (logout)
)

urlpatterns = [

    path('',home, name='home'),  # Home page view
    # User registration endpoint (signup)
    path('signup/', RegisterView.as_view(), name='signup'),

    # JWT login endpoint - returns access and refresh tokens after user credentials verified
    path('login/', TokenObtainPairView.as_view(), name='login'),

    # Refresh JWT access token endpoint using a valid refresh token
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Logout endpoint to blacklist the refresh token, effectively logging out user
    path('logout/', TokenBlacklistView.as_view(), name='logout'),

    # Retrieve, update, or delete the logged-in user's profile details
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),

    # Create user profile endpoint (for logged-in users)
    path('profile/create/', UserProfileCreateView.as_view(), name='create-user-profile'),

     # Create diabetic profile
    path('diabetic/create/', DiabeticProfileCreateView.as_view(), name='create-diabetic-profile'),

    # Get, update, or delete diabetic profile
    path('diabetic/', DiabeticProfileDetailView.as_view(), name='diabetic-profile'),
]
    


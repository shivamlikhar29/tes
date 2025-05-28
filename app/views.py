from django.shortcuts import render, HttpResponse
from rest_framework import generics, permissions
from .models import User, UserProfile, DiabeticProfile
from .serializers import RegisterSerializer, UserProfileSerializer,DiabeticProfileSerializer

# Create your views here.

class RegisterView(generics.CreateAPIView):
    """
    API view to handle user registration.
    Allows clients to create a new user by sending POST request with email and password.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete the authenticated user's profile.
    - GET: Retrieve the current user's profile data.
    - PUT/PATCH: Update the current user's profile.
    - DELETE: Delete the current user's profile.
    Requires the user to be authenticated.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Returns the UserProfile object associated with the current logged-in user.
        Throws error if not found.
        """
        return UserProfile.objects.get(user=self.request.user)


class UserProfileCreateView(generics.CreateAPIView):
    """
    API view to create a new UserProfile for the authenticated user.
    Accepts profile data in POST request.
    Links the created profile with the current logged-in user automatically.
    Requires the user to be authenticated.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Overrides creation to attach the current user to the profile before saving.
        """
        serializer.save(user=self.request.user)




class DiabeticProfileCreateView(generics.CreateAPIView):
    """
    API view to create a DiabeticProfile for the authenticated user.
    Requires authentication.
    """
    serializer_class = DiabeticProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_profile = self.request.user.userprofile
        serializer.save(user_profile=user_profile)


class DiabeticProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete the authenticated user's DiabeticProfile.
    Requires authentication.
    """
    serializer_class = DiabeticProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return DiabeticProfile.objects.get(user_profile__user=self.request.user)

def home(request):
    """
    A simple HTTP view to return a basic greeting message.
    Useful for testing if the server is running.
    """
    return HttpResponse("Hello, world! This is the home page.")

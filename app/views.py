from django.shortcuts import render, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from .models import User, UserProfile, DiabeticProfile,UserMeal
from .serializers import RegisterSerializer, UserProfileSerializer,DiabeticProfileSerializer,UserMealSerializer

# Create your views here.


def home(request):
    """
    A simple HTTP view to return a basic greeting message.
    Useful for testing if the server is running.
    """
    return HttpResponse("Hello, world! This is the home page.")

class RegisterView(generics.CreateAPIView):
    """
    API view to handle user registration.
    Allows clients to create a new user by sending POST request with email and password.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


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

#Meals Log CRUD API Views
# class UserMealViewSet(viewsets.ModelViewSet):
#     serializer_class = UserMealSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # Only return meals of the logged-in user
#         return UserMeal.objects.filter(user=self.request.user).order_by('-consumed_at')


# Create View
class UserMealListCreateView(generics.ListCreateAPIView):
    queryset = UserMeal.objects.all()
    serializer_class = UserMealSerializer

# Retrieve, Update, Delete View
class UserMealDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserMeal.objects.all()
    serializer_class = UserMealSerializer

#------------------CALORIE TRACKER API ENDPOINTS----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_calories(request):
    try:
        profile = UserProfile.objects.get(user=request.user)

        weight = profile.weight_kg
        height = profile.height_cm
        age = profile.age
        gender = profile.gender
        activity_level = profile.activity_level
        goal = profile.goal

        # Calculate BMR
        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # Activity multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }

        activity_multiplier = activity_multipliers.get(activity_level, 1.2)

        # Adjust for goal
        maintenance_calories = bmr * activity_multiplier

        if goal == "lose_weight":
            recommended_calories = maintenance_calories - 500
        elif goal == "gain_weight":
            recommended_calories = maintenance_calories + 500
        else:
            recommended_calories = maintenance_calories

        return Response({
            "recommended_calories": round(recommended_calories),
            "goal": goal,
            "activity_level": activity_level,
            "bmr": round(bmr),
        })

    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)


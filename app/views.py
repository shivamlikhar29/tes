from django.shortcuts import render, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
from rest_framework.exceptions import ValidationError   
from utils.utils import UNIT_TO_GRAMS
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from datetime import timedelta
from django.utils.timezone import now
from rest_framework import status
from rest_framework import generics, permissions
from .models import User, UserProfile, DiabeticProfile,UserMeal,FoodItem
from .serializers import RegisterSerializer, UserProfileSerializer,DiabeticProfileSerializer,UserMealSerializer
from django.http import HttpResponseForbidden

# Create your views here.

####################################DECORATORS####################################

def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.role not in allowed_roles:
                return HttpResponseForbidden("Access Denied")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
#####################################DECORATORS####################################

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


class UserMealViewSet(viewsets.ModelViewSet):
    serializer_class = UserMealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserMeal.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        if isinstance(data, dict):  # Single object
            data = [data]

        response_data = []

        for item in data:
            serializer = self.get_serializer(data=item)
            serializer.is_valid(raise_exception=True)

            food_name = serializer.validated_data.get("food_name")
            quantity = serializer.validated_data.get("quantity")
            unit = serializer.validated_data.get("unit").lower()
            meal_type = serializer.validated_data.get("meal_type")

            try:
                food_item = FoodItem.objects.get(name__iexact=food_name)
            except FoodItem.DoesNotExist:
                raise ValidationError(f"Food item '{food_name}' not found in database.")

            grams_per_unit = UNIT_TO_GRAMS.get(unit, 100)
            weight_in_grams = quantity * grams_per_unit

            calories = (weight_in_grams / 100) * food_item.calories
            protein = (weight_in_grams / 100) * food_item.protein_g
            carbs = (weight_in_grams / 100) * food_item.carbs_g
            fats = (weight_in_grams / 100) * food_item.fats_g
            sugar = (weight_in_grams / 100) * food_item.sugar_g
            fiber = (weight_in_grams / 100) * food_item.fiber_g

            instance = serializer.save(
                user=user,
                food_item=food_item,
                food_name=food_item.name,
                calories=round(calories, 2),
                protein=round(protein, 2),
                carbs=round(carbs, 2),
                fats=round(fats, 2),
                sugar=round(sugar, 2),
                fiber=round(fiber, 2),
            )

            response_data.append(self.get_serializer(instance).data)

        return Response(response_data, status=status.HTTP_201_CREATED)


#------------------CALORIE RECOMMEND API ENDPOINTS----------------
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

##########################CALORIE TRACKER API ENDPOINTS END##########################
class DailyCalorieSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = now().date()
        meals_today = UserMeal.objects.filter(user=request.user, date=today)

        totals = meals_today.aggregate(
            total_calories=Sum("calories"),
            total_protein=Sum("protein"),
            total_carbs=Sum("carbs"),
            total_fats=Sum("fats"),
            total_sugar=Sum("sugar"),
            total_fiber=Sum("fiber"),
        )

        return Response({
            "date": today,
            "calories": totals["total_calories"] or 0,
            "protein": totals["total_protein"] or 0,
            "carbs": totals["total_carbs"] or 0,
            "fats": totals["total_fats"] or 0,
            "sugar": totals["total_sugar"] or 0,
            "fiber": totals["total_fiber"] or 0,
        })


##############################################USER TYPES ROLES ACTORS##############################################
class OperatorDashboardView(APIView):
    @role_required(["operator"])
    def get(self, request):
        # Sample: dummy contact report
        contacts = [
            {"name": "Shivam", "mobile": "9999999999"},
            {"name": "Ritik", "mobile": "8888888888"}
        ]
        return Response({"contacts": contacts, "message": "Operator access granted"}, status=status.HTTP_200_OK)

class NutritionistDashboardView(APIView):
    @role_required(["nutritionist"])
    def get(self, request):
        # Example: get all patient profiles (in real case, only assigned ones)
        patients = UserProfile.objects.filter(user__role="user")
        data = UserProfileSerializer(patients, many=True).data
        return Response({"patients": data}, status=status.HTTP_200_OK)

class OwnerDashboardView(APIView):
    @role_required(["owner"])
    def get(self, request):
        today = now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Sample business metrics
        total_users = User.objects.count()
        active_patients = UserProfile.objects.filter(user__role="user").count()
        new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
        new_users_month = User.objects.filter(date_joined__gte=month_ago).count()

        # Dummy revenue logic — replace with real billing if needed
        estimated_revenue = active_patients * 49  # Rs 49 per user/month, as an example

        return Response({
            "total_users": total_users,
            "active_patients": active_patients,
            "new_users_last_week": new_users_week,
            "new_users_last_month": new_users_month,
            "estimated_revenue": f"₹{estimated_revenue}",
            "message": "Owner dashboard access granted"
        }, status=status.HTTP_200_OK)
from django.shortcuts import render, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
from django.db.models import Count
from rest_framework.exceptions import ValidationError   
from utils.utils import UNIT_TO_GRAMS,role_required
from datetime import datetime, time
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail
from rest_framework import status
from rest_framework import generics, permissions
from .models import User, UserProfile, DiabeticProfile,UserMeal,FoodItem,PatientReminder, NutritionistProfile, DietRecommendation
from .serializers import RegisterSerializer, UserProfileSerializer,DiabeticProfileSerializer,UserMealSerializer,PatientReminderSerializer, NutritionistProfileSerializer, DietRecommendationSerializer


# Create your views here.

####################################DECORATORS####################################
#####################################DECORATORS###################################

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


class DiabeticProfileListView(generics.ListAPIView):
    """
    API view to list all diabetic reports of the authenticated user.
    """
    serializer_class = DiabeticProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiabeticProfile.objects.filter(user_profile__user=self.request.user)


class DiabeticProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific DiabeticProfile report of the authenticated user.
    Requires authentication.
    """
    serializer_class = DiabeticProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return DiabeticProfile.objects.filter(user_profile__user=self.request.user)

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
                meal_type=meal_type,
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
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        meals_today = UserMeal.objects.filter(user=request.user, consumed_at__range=(start, end))


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

class OwnerDashboardView(APIView):
    @role_required(["owner"])
    def get(self, request):
        today = now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Core Metrics
        total_users = User.objects.filter(role="user").count()
        new_users_week = User.objects.filter(role="user", date_joined__gte=week_ago).count()
        new_users_month = User.objects.filter(role="user", date_joined__gte=month_ago).count()
        active_patients = UserMeal.objects.filter(date__gte=week_ago).values("user").distinct().count()

        estimated_revenue = active_patients * 49
        meals_logged_week = UserMeal.objects.filter(date__gte=week_ago).count()
        meals_logged_month = UserMeal.objects.filter(date__gte=month_ago).count()
        

        # Country-wise User Count
        users_by_country = (
            UserProfile.objects.values("country")
            .annotate(user_count=Count("id"))
            .order_by("-user_count")
        )

        # Dummy promotion and feedback placeholder
        feedbacks = 0
        promotions = [
            {"campaign": "Instagram Ad", "reach": "10k+", "status": "Running"},
            {"campaign": "Referral Program", "reach": "5k+", "status": "Ended"},
        ]

        return Response({
            "date": str(today),
            "user_stats": {
                "total_users": total_users,
                "new_users_week": new_users_week,
                "new_users_month": new_users_month,
                "active_patients_week": active_patients,
            },
            "usage": {
                "meals_logged_week": meals_logged_week,
                "meals_logged_month": meals_logged_month,
            },
            "revenue": f"₹{estimated_revenue}",
            "users_by_country": users_by_country,
            "feedback_collected": feedbacks,
            "promotions": promotions,
            "message": "Owner dashboard data fetched successfully"
        }, status=status.HTTP_200_OK)

##############################################OPERATOR DASHBOARD VIEW#################################################################
class IsOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "operator"


# Create & list reminders
class ReminderListCreateView(generics.ListCreateAPIView):
    queryset = PatientReminder.objects.all()
    serializer_class = PatientReminderSerializer
    permission_classes = [IsOperator]

#
class SendReminderView(APIView):
    permission_classes = [IsOperator]

    def post(self, request, pk):
        try:
            reminder = PatientReminder.objects.get(pk=pk)
            # Simulate sending email/SMS
            reminder.sent = True
            reminder.save()

            # Optional: Send email (only if you set up SMTP)
            # send_mail(
            #     subject="Health Reminder",
            #     message=reminder.message,
            #     from_email="admin@yourapp.com",
            #     recipient_list=[reminder.user.email],
            # )

            return Response({"status": "Reminder sent!"})
        except PatientReminder.DoesNotExist:
            return Response({"error": "Reminder not found"}, status=status.HTTP_404_NOT_FOUND)


# Get all users' contact info
class UserContactListView(generics.ListAPIView):
    permission_classes = [IsOperator]

    def get(self, request):
        users = User.objects.filter(role="user")
        data = []

        for u in users:
            # Check if user has a profile before accessing it
            if hasattr(u, "userprofile"):
                profile = u.userprofile
                data.append({
                    "id": u.id,
                    "email": u.email,
                    "contact_number": profile.mobile_number,  # assuming contact_number is here
                    "country": profile.country,
                })
            else:
                # fallback if profile missing
                data.append({
                    "id": u.id,
                    "email": u.email,
                    "contact_number": None,
                    "country": None,
                })

        return Response(data)


#  Compile report (basic version for Owner)
class OperatorReportView(APIView):
    permission_classes = [IsOperator]

    def get(self, request):
        user_count = User.objects.filter(role="user").count()
        # reminders_sent = PatientReminder.objects.filter(sent_at=True).count()
        reminders_sent = PatientReminder.objects.exclude(sent_at=None).count()
        return Response({
            "total_users": user_count,
            "reminders_sent": reminders_sent,
        })
    
#########################################################################################################################################

############ Nutritionist Dashboard View
class IsNutritionistWithAccess(permissions.BasePermission):
    """
    Allow only Nutritionists with proper expert_level to access assigned users' diet recommendations.
    """

    def has_permission(self, request, view):
        return hasattr(request.user, 'nutritionistprofile')

    def has_object_permission(self, request, view, obj):
        profile = request.user.nutritionistprofile
        if profile.expert_level == 1:
            return obj.user.id in range(1, 11)
        elif profile.expert_level == 2:
            return obj.user.id in range(11, 21)
        return False

# For Nutritionist - List + Create
class DietRecommendationListCreateView(generics.ListCreateAPIView):
    queryset = DietRecommendation.objects.all().order_by('-created_at')
    serializer_class = DietRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNutritionistWithAccess]

    def get_queryset(self):
        profile = self.request.user.nutritionistprofile
        if profile.expert_level == 1:
            return self.queryset.filter(user__id__range=(1, 10))
        elif profile.expert_level == 2:
            return self.queryset.filter(user__id__range=(11, 20))
        return DietRecommendation.objects.none()

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError("User with provided ID does not exist.")

        # Check access before allowing creation
        profile = self.request.user.nutritionistprofile
        if profile.expert_level == 1 and user.id not in range(1, 11):
            raise ValidationError("You do not have access to this user.")
        elif profile.expert_level == 2 and user.id not in range(11, 21):
            raise ValidationError("You do not have access to this user.")
        
        serializer.save(created_by=self.request.user, user=user)


# For Nutritionist - Retrieve, Update, Delete
class DietRecommendationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DietRecommendation.objects.all()
    serializer_class = DietRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNutritionistWithAccess]

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

# For Users - List only their own recommendations
class UserDietRecommendationListView(generics.ListAPIView):
    serializer_class = DietRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DietRecommendation.objects.filter(user=self.request.user).order_by('-created_at')

    queryset = DietRecommendation.objects.all()
    serializer_class = DietRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNutritionistWithAccess]
    # permission_classes = [permissions.IsAuthenticated]
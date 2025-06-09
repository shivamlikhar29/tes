from rest_framework import serializers
from .models import User, UserProfile, DiabeticProfile,UserMeal, PatientReminder, FoodItem, NutritionistProfile, DietRecommendation



# Serializer for UserProfile model to convert it to JSON and validate incoming data
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    Converts UserProfile model instances to JSON and validates incoming data.
    Excludes the 'user' field because it's set automatically in the view.
    """
    class Meta:
        model = UserProfile
        exclude = ['user']  # Exclude the user field since it's linked automatically

# Serializer for User model registration
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for User model registration.
    Includes nested UserProfileSerializer to create both User and UserProfile in one request.
    """

    class Meta:
        model = User
        fields = ['email', 'password']  # Include email, password, and profile
        extra_kwargs = {'password': {'write_only': True}}  # Password write-only for security

    def create(self, validated_data):
        """ 
        Create a new User instance and related UserProfile instance.
        - Extract nested profile data from validated_data.
        - Create the user using custom user manager.
        - Create the user profile linked to the created user.
        """
        user = User.objects.create_user(**validated_data)  # Create user with email and password
        return user

# Serializer to convert DiabeticProfile model to JSON and validate incoming data
class DiabeticProfileSerializer(serializers.ModelSerializer):
    user_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = DiabeticProfile
        fields = '__all__'  # Includes all fields from the model

# Serializer for UserMeal model to handle meal logging
class UserMealSerializer(serializers.ModelSerializer):
    
    food_name = serializers.CharField()
    meal_type = serializers.ChoiceField(choices=["lunch", "breakfast", "dinner", "snack"])

    class Meta:
        model = UserMeal
        fields = [
            "id", "food_name", "meal_type", "unit", "quantity", "calories",
            "protein", "carbs", "fats", "sugar", "fiber",
            "consumed_at", "remarks", "date"
        ]
        read_only_fields = [
            "calories", "protein", "carbs", "fats", "sugar", "fiber", "consumed_at", "date"
        ]

# Serializer for PatientReminder model to handle reminders
class PatientReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientReminder
        fields = '__all__'







# Serializer for FoodItem model to handle food items
class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'calories']

# Serializer for NutritionistProfile model to handle nutritionist profiles
class NutritionistProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = NutritionistProfile
        fields = ['id', 'user', 'expert_level']

# Serializer for DietRecommendation model to handle diet recommendations
class DietRecommendationSerializer(serializers.ModelSerializer):
    recommended_foods = FoodItemSerializer(many=True, read_only=True)
    recommended_foods_ids = serializers.PrimaryKeyRelatedField(
        queryset=FoodItem.objects.all(), many=True, write_only=True, source='recommended_foods'
    )
    created_by = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')

    class Meta:
        model = DietRecommendation
        fields = [
            'id', 'user', 'user_id', 'recommended_foods', 'recommended_foods_ids', 'type',
            'created_at', 'created_by', 'notes', 'reason', 'sugar_limit_g', 'glycemic_index_note'
        ]















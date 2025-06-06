from rest_framework import serializers
from .models import User, UserProfile, DiabeticProfile,UserMeal

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    Converts UserProfile model instances to JSON and validates incoming data.
    Excludes the 'user' field because it's set automatically in the view.
    """
    class Meta:
        model = UserProfile
        exclude = ['user']  # Exclude the user field since it's linked automatically


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


# CRUD API FOR MEALS LOGS
class UserMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMeal
        fields = '__all__'
        read_only_fields = ['user']  # Prevent clients from sending user manually

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



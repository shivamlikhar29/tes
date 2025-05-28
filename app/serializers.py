from rest_framework import serializers
from .models import User, UserProfile, DiabeticProfile

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
    userprofile = UserProfileSerializer()  # Nested serializer for user profile data

    class Meta:
        model = User
        fields = ['email', 'password', 'userprofile']  # Include email, password, and profile
        extra_kwargs = {'password': {'write_only': True}}  # Password write-only for security

    def create(self, validated_data):
        """
        Create a new User instance and related UserProfile instance.
        - Extract nested profile data from validated_data.
        - Create the user using custom user manager.
        - Create the user profile linked to the created user.
        """
        profile_data = validated_data.pop('userprofile')  # Remove profile data from user data
        user = User.objects.create_user(**validated_data)  # Create user with email and password
        UserProfile.objects.create(user=user, **profile_data)  # Create linked profile with extra data
        return user

# Serializer to convert DiabeticProfile model to JSON and validate incoming data
class DiabeticProfileSerializer(serializers.ModelSerializer):
    user_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = DiabeticProfile
        fields = '__all__'  # Includes all fields from the model
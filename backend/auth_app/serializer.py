from rest_framework import serializers
from .models import UserProfile


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = UserProfile
        fields = ["email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        return UserProfile.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "email", "first_name", "last_name", "date_joined")
        read_only_fields = ("id", "date_joined")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

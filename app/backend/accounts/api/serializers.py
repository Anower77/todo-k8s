from rest_framework import serializers
from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        from accounts.services.auth_service import register_user
        return register_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]
        read_only_fields = ["id"]

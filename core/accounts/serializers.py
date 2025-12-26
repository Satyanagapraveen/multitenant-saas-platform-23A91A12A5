from rest_framework import serializers
from tenants.models import Tenant
from accounts.models import User

from rest_framework import serializers
from accounts.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'full_name', 'role')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role', 'is_active', 'created_at')


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'role', 'is_active')


class TenantRegisterSerializer(serializers.Serializer):
    tenantName = serializers.CharField()
    subdomain = serializers.CharField()
    adminEmail = serializers.EmailField()
    adminPassword = serializers.CharField(min_length=8)
    adminFullName = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    tenantSubdomain = serializers.CharField()

from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            'id',
            'name',
            'subdomain',
            'status',
            'subscription_plan',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TenantDetailSerializer(serializers.ModelSerializer):
    subscriptionPlan = serializers.CharField(source='subscription_plan')
    maxUsers = serializers.IntegerField(source='max_users')
    maxProjects = serializers.IntegerField(source='max_projects')
    createdAt = serializers.DateTimeField(source='created_at')
    updatedAt = serializers.DateTimeField(source='updated_at')
    
    class Meta:
        model = Tenant
        fields = [
            'id',
            'name',
            'subdomain',
            'status',
            'subscriptionPlan',
            'maxUsers',
            'maxProjects',
            'createdAt',
            'updatedAt'
        ]
        read_only_fields = fields

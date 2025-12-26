from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True, allow_null=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'tenant',
            'tenant_name',
            'user',
            'user_email',
            'user_name',
            'action',
            'entity_type',
            'entity_id',
            'ip_address',
            'created_at'
        ]
        read_only_fields = fields

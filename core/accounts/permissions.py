from rest_framework.permissions import BasePermission

class IsTenantAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'tenant_admin'

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'super_admin'

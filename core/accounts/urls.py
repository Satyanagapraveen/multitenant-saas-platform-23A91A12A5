from django.urls import path
from accounts.views import (
    register_tenant,
    login,
    logout,
    add_user_to_tenant,
    list_tenant_users,
    update_or_delete_user,
)
from accounts.views import me


urlpatterns = [
    path('auth/register-tenant', register_tenant),
    path('auth/login', login),
    path('auth/logout', logout),
    path('auth/me', me),


    path('tenants/<uuid:tenant_id>/users', add_user_to_tenant),
    path('tenants/<uuid:tenant_id>/users/list', list_tenant_users),

    path('users/<uuid:user_id>', update_or_delete_user),
]

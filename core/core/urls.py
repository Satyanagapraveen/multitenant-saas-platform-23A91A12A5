"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,include
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """Health check endpoint for Docker and load balancers"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        # Return 503 if database is not connected
        return JsonResponse({
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }, status=503)
    
    return JsonResponse({
        "status": "ok",
        "database": db_status
    })


def api_root(request):
    """Root endpoint - API information"""
    return JsonResponse({
        "name": "Multi-Tenant SaaS API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "auth": {
                "register": "POST /api/auth/register-tenant",
                "login": "POST /api/auth/login",
                "logout": "POST /api/auth/logout",
                "me": "GET /api/auth/me"
            },
            "tenants": "/api/tenants/",
            "users": "/api/tenants/{id}/users",
            "projects": "/api/projects",
            "tasks": "/api/tasks",
            "audit_logs": "/api/audit-logs/"
        },
        "documentation": "See README.md for full API documentation"
    })


urlpatterns = [
    path("", api_root, name='api_root'),
    path("admin/", admin.site.urls),
    path('api/health', health_check, name='health_check'),
    path('api/', include('accounts.urls')),
    path('api/', include('projects.urls')),
    path('api/', include('tasks.urls')),
    path('api/tenants/', include('tenants.urls')),
    path('api/audit-logs/', include('audit_logs.urls')),
]

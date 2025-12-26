from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from tenants.models import Tenant
from accounts.models import User
from accounts.serializers import TenantRegisterSerializer, LoginSerializer,UserListSerializer,CreateUserSerializer,UpdateUserSerializer
from accounts.permissions import IsTenantAdmin
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes
)
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user

    return Response({
        "success": True,
        "data": {
            "id": str(user.id),
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role,
            "tenantId": str(user.tenant.id) if user.tenant else None
        }
    })


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_or_delete_user(request, user_id):
    user = request.user
    target_user = get_object_or_404(User, id=user_id)

    # Tenant isolation
    if user.tenant != target_user.tenant:
        return Response({"message": "Forbidden"}, status=403)

    # ================= UPDATE =================
    if request.method == 'PUT':
        if user != target_user and user.role != 'tenant_admin':
            return Response({"message": "Not authorized"}, status=403)

        if 'full_name' in request.data:
            target_user.full_name = request.data['full_name']

        if user.role == 'tenant_admin':
            if 'role' in request.data:
                target_user.role = request.data['role']
            if 'is_active' in request.data:
                target_user.is_active = request.data['is_active']

        target_user.save()

        return Response({
            "success": True,
            "message": "User updated successfully",
            "data": {
                "id": target_user.id,
                "full_name": target_user.full_name,
                "role": target_user.role,
                "is_active": target_user.is_active
            }
        })

    # ================= DELETE =================
    if request.method == 'DELETE':
        if user.role != 'tenant_admin':
            return Response({"message": "Not authorized"}, status=403)

        if user.id == target_user.id:
            return Response(
                {"message": "Tenant admin cannot delete themselves"},
                status=403
            )

        target_user.delete()

        return Response({
            "success": True,
            "message": "User deleted successfully"
        })



@api_view(['POST'])
def add_user_to_tenant(request, tenant_id):
    user = request.user

    if user.role != 'tenant_admin':
        return Response({"message": "Not authorized"}, status=403)

    if user.tenant.id != tenant_id:
        return Response({"message": "Invalid tenant"}, status=403)

    tenant = user.tenant

    # ✅ USER LIMIT CHECK
    if User.objects.filter(tenant=tenant).count() >= tenant.max_users:
        return Response({"message": "User limit reached"}, status=403)

    # ✅ EMAIL UNIQUENESS CHECK (IMPORTANT FIX)
    if User.objects.filter(email=request.data.get('email'), tenant=tenant).exists():
        return Response(
            {"message": "Email already exists in this tenant"},
            status=409
        )

    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    new_user = serializer.save(tenant=tenant)

    return Response({
        "success": True,
        "message": "User created successfully",
        "data": UserListSerializer(new_user).data
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tenant_users(request, tenant_id):
    current_user = request.user

    # ✅ Tenant isolation
    if not current_user.tenant or current_user.tenant.id != tenant_id:
        return Response({"message": "Unauthorized"}, status=403)

    qs = User.objects.filter(tenant=current_user.tenant)

    # 🔍 Search by email or full name
    search = request.GET.get('search')
    if search:
        qs = qs.filter(
            Q(email__icontains=search) |
            Q(full_name__icontains=search)
        )

    # 🎭 Filter by role
    role = request.GET.get('role')
    if role:
        qs = qs.filter(role=role)

    qs = qs.order_by('-created_at')

    return Response({
        "success": True,
        "data": {
            "users": UserListSerializer(qs, many=True).data,
            "total": qs.count()
        }
    })



@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def register_tenant(request):
    serializer = TenantRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    with transaction.atomic():
        tenant = Tenant.objects.create(
            name=data['tenantName'],
            subdomain=data['subdomain'],
            subscription_plan='free',
            max_users=5,
            max_projects=3
        )

        admin = User.objects.create_user(
            email=data['adminEmail'],
            password=data['adminPassword'],
            full_name=data['adminFullName'],
            role='tenant_admin',
            tenant=tenant
        )

    return Response({
        "success": True,
        "message": "Tenant registered successfully",
        "data": {
            "tenantId": tenant.id,
            "subdomain": tenant.subdomain,
            "adminUser": {
                "id": admin.id,
                "email": admin.email,
                "role": admin.role
            }
        }
    }, status=201)

@api_view(['POST'])
@authentication_classes([]) 
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    subdomain = serializer.validated_data['tenantSubdomain']

    try:
        tenant = Tenant.objects.get(subdomain=subdomain)
    except Tenant.DoesNotExist:
        return Response(
            {"message": "Tenant not found"},
            status=404
        )

    user = User.objects.filter(
        email=email,
        tenant=tenant,
        is_active=True
    ).first()

    if not user or not user.check_password(password):
        return Response(
            {"message": "Invalid credentials"},
            status=401
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "success": True,
        "data": {
            "id": str(user.id),
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role,
            "tenantId": str(tenant.id),
            "token": str(refresh.access_token),
            "expiresIn": 86400
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint. For JWT-only auth, this is mainly for audit logging
    since the client is responsible for removing the token.
    """
    from audit_logs.utils import log_action, AuditActions
    
    # Log the logout action
    log_action(
        request=request,
        action=AuditActions.USER_LOGOUT,
        entity_type='user',
        entity_id=request.user.id
    )
    
    return Response({
        "success": True,
        "message": "Logged out successfully"
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import Tenant
from .serializers import TenantSerializer, TenantDetailSerializer
from accounts.models import User
from projects.models import Project
from tasks.models import Task
from audit_logs.utils import log_action, AuditActions


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tenants(request):
    """
    List all tenants - super_admin only.
    Supports pagination and filtering by status and subscription_plan.
    """
    user = request.user
    
    # Only super_admin can list all tenants
    if user.role != 'super_admin':
        return Response({
            'success': False,
            'message': 'Access denied. Super admin only.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    queryset = Tenant.objects.all()
    
    # Filter by status
    tenant_status = request.query_params.get('status')
    if tenant_status:
        queryset = queryset.filter(status=tenant_status)
    
    # Filter by subscription_plan
    plan = request.query_params.get('subscriptionPlan')
    if plan:
        queryset = queryset.filter(subscription_plan=plan)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    limit = min(int(request.query_params.get('limit', 10)), 100)
    offset = (page - 1) * limit
    
    total = queryset.count()
    tenants = queryset.order_by('-created_at')[offset:offset + limit]
    
    # Build response with stats
    tenants_data = []
    for tenant in tenants:
        tenant_data = TenantSerializer(tenant).data
        tenant_data['totalUsers'] = User.objects.filter(tenant=tenant).count()
        tenant_data['totalProjects'] = Project.objects.filter(tenant=tenant).count()
        tenants_data.append(tenant_data)
    
    return Response({
        'success': True,
        'data': {
            'tenants': tenants_data,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit if total > 0 else 1,
                'totalTenants': total,
                'limit': limit
            }
        }
    })


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def tenant_detail(request, tenant_id):
    """
    GET: Get tenant details with stats
    PUT: Update tenant (tenant_admin can update name only, super_admin can update all)
    """
    user = request.user
    
    # Get the tenant
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tenant not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Authorization: User must belong to tenant OR be super_admin
    if user.role != 'super_admin' and (not user.tenant or str(user.tenant.id) != str(tenant_id)):
        return Response({
            'success': False,
            'message': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        # Calculate stats
        total_users = User.objects.filter(tenant=tenant).count()
        total_projects = Project.objects.filter(tenant=tenant).count()
        total_tasks = Task.objects.filter(tenant=tenant).count()
        
        serializer = TenantDetailSerializer(tenant)
        data = serializer.data
        data['stats'] = {
            'totalUsers': total_users,
            'totalProjects': total_projects,
            'totalTasks': total_tasks
        }
        
        return Response({
            'success': True,
            'data': data
        })
    
    elif request.method == 'PUT':
        # tenant_admin can only update name
        if user.role == 'tenant_admin':
            allowed_fields = ['name']
            restricted_fields = ['status', 'subscription_plan', 'max_users', 'max_projects', 'subdomain']
            
            for field in restricted_fields:
                if field in request.data:
                    return Response({
                        'success': False,
                        'message': f'You are not authorized to update {field}'
                    }, status=status.HTTP_403_FORBIDDEN)
            
            # Only update name
            if 'name' in request.data:
                tenant.name = request.data['name']
                tenant.save()
        
        elif user.role == 'super_admin':
            # Super admin can update all fields
            if 'name' in request.data:
                tenant.name = request.data['name']
            if 'status' in request.data:
                tenant.status = request.data['status']
            if 'subscription_plan' in request.data:
                tenant.subscription_plan = request.data['subscription_plan']
                # Update limits based on plan
                if request.data['subscription_plan'] == 'free':
                    tenant.max_users = 5
                    tenant.max_projects = 3
                elif request.data['subscription_plan'] == 'pro':
                    tenant.max_users = 20
                    tenant.max_projects = 20
                elif request.data['subscription_plan'] == 'enterprise':
                    tenant.max_users = 100
                    tenant.max_projects = 100
            if 'max_users' in request.data:
                tenant.max_users = request.data['max_users']
            if 'max_projects' in request.data:
                tenant.max_projects = request.data['max_projects']
            tenant.save()
        
        else:
            return Response({
                'success': False,
                'message': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Log the action
        log_action(
            request=request,
            action=AuditActions.UPDATE_TENANT,
            entity_type='tenant',
            entity_id=tenant.id,
            tenant=tenant
        )
        
        serializer = TenantDetailSerializer(tenant)
        return Response({
            'success': True,
            'message': 'Tenant updated successfully',
            'data': serializer.data
        })


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import AuditLog
from .serializers import AuditLogSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_audit_logs(request):
    """
    List audit logs for the current tenant.
    Super admins can see all logs, tenant admins see their tenant's logs.
    Supports filtering by action, entity_type, and date range.
    """
    user = request.user
    
    # Base queryset
    if user.role == 'super_admin':
        queryset = AuditLog.objects.all()
    else:
        queryset = AuditLog.objects.filter(tenant=user.tenant)
    
    # Filter by action
    action = request.query_params.get('action')
    if action:
        queryset = queryset.filter(action=action)
    
    # Filter by entity_type
    entity_type = request.query_params.get('entity_type')
    if entity_type:
        queryset = queryset.filter(entity_type=entity_type)
    
    # Filter by user_id
    user_id = request.query_params.get('user_id')
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    
    # Filter by date range
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    limit = min(int(request.query_params.get('limit', 50)), 100)
    offset = (page - 1) * limit
    
    total = queryset.count()
    logs = queryset.order_by('-created_at')[offset:offset + limit]
    
    serializer = AuditLogSerializer(logs, many=True)
    
    return Response({
        'success': True,
        'data': {
            'logs': serializer.data,
            'total': total,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'limit': limit
            }
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audit_log(request, log_id):
    """Get a single audit log entry by ID"""
    user = request.user
    
    try:
        if user.role == 'super_admin':
            log = AuditLog.objects.get(id=log_id)
        else:
            log = AuditLog.objects.get(id=log_id, tenant=user.tenant)
    except AuditLog.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Audit log not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AuditLogSerializer(log)
    
    return Response({
        'success': True,
        'data': serializer.data
    })


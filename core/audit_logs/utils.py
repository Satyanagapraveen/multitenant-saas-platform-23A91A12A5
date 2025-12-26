from .models import AuditLog


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_action(request, action, entity_type, entity_id, tenant=None, user=None):
    """
    Create an audit log entry.
    
    Args:
        request: The HTTP request object (for IP address)
        action: The action performed (e.g., 'CREATE_USER', 'DELETE_PROJECT')
        entity_type: The type of entity (e.g., 'user', 'project', 'task')
        entity_id: The ID of the entity
        tenant: The tenant (optional, will use request user's tenant if not provided)
        user: The user (optional, will use request user if not provided)
    
    Returns:
        AuditLog instance
    """
    if user is None and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
    
    if tenant is None and user and hasattr(user, 'tenant'):
        tenant = user.tenant
    
    ip_address = get_client_ip(request) if request else None
    
    audit_log = AuditLog.objects.create(
        tenant=tenant,
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        ip_address=ip_address
    )
    
    return audit_log


# Common action constants
class AuditActions:
    # User actions
    USER_LOGIN = 'USER_LOGIN'
    USER_LOGOUT = 'USER_LOGOUT'
    USER_REGISTER = 'USER_REGISTER'
    CREATE_USER = 'CREATE_USER'
    UPDATE_USER = 'UPDATE_USER'
    DELETE_USER = 'DELETE_USER'
    
    # Tenant actions
    CREATE_TENANT = 'CREATE_TENANT'
    UPDATE_TENANT = 'UPDATE_TENANT'
    DELETE_TENANT = 'DELETE_TENANT'
    
    # Project actions
    CREATE_PROJECT = 'CREATE_PROJECT'
    UPDATE_PROJECT = 'UPDATE_PROJECT'
    DELETE_PROJECT = 'DELETE_PROJECT'
    
    # Task actions
    CREATE_TASK = 'CREATE_TASK'
    UPDATE_TASK = 'UPDATE_TASK'
    UPDATE_TASK_STATUS = 'UPDATE_TASK_STATUS'
    DELETE_TASK = 'DELETE_TASK'

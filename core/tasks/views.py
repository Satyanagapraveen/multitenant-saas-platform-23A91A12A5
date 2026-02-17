from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from tasks.models import Task
from tasks.serializers import (
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateSerializer
)
from projects.models import Project
from accounts.models import User

# API 16 + 17
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def project_tasks(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    is_super_admin = request.user.role == 'super_admin'

    # Tenant isolation (super admin can access all)
    if not is_super_admin and project.tenant != request.user.tenant:
        return Response({"message": "Forbidden"}, status=403)

    # ---------- CREATE TASK ----------
    if request.method == 'POST':
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assigned_user = serializer.validated_data.get('assigned_to')
        if assigned_user and assigned_user.tenant != request.user.tenant:
            return Response(
                {"message": "Assigned user must belong to same tenant"},
                status=400
            )

        task = serializer.save(
            project=project,
            tenant=project.tenant
        )

        return Response({
            "success": True,
            "data": TaskListSerializer(task).data
        }, status=201)

    # ---------- LIST TASKS ----------
    tasks = Task.objects.filter(project=project)

    # Filters
    status = request.GET.get('status')
    assigned_to = request.GET.get('assignedTo')
    priority = request.GET.get('priority')
    search = request.GET.get('search')

    if status:
        tasks = tasks.filter(status=status)
    if assigned_to:
        tasks = tasks.filter(assigned_to_id=assigned_to)
    if priority:
        tasks = tasks.filter(priority=priority)
    if search:
        tasks = tasks.filter(title__icontains=search)

    tasks = tasks.order_by('-priority', 'due_date')

    serializer = TaskListSerializer(tasks, many=True)
    return Response({
        "success": True,
        "data": {
            "tasks": serializer.data,
            "total": tasks.count()
        }
    })


# API 18
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    is_super_admin = request.user.role == 'super_admin'

    # Tenant isolation (super admin can access all)
    if not is_super_admin and task.tenant != request.user.tenant:
        return Response({"message": "Forbidden"}, status=403)

    # Permission: Only assigned user or admin can update status
    is_admin = request.user.role == 'tenant_admin'
    is_assignee = task.assigned_to == request.user
    
    if not is_admin and not is_assignee:
        return Response(
            {"message": "Only the assigned user or admin can update this task"},
            status=403
        )

    status_value = request.data.get('status')
    if status_value not in ['todo', 'in_progress', 'completed']:
        return Response({"message": "Invalid status"}, status=400)

    task.status = status_value
    task.save()

    return Response({
        "success": True,
        "data": {
            "id": task.id,
            "status": task.status,
            "updatedAt": task.updated_at
        }
    })


# API 19
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    is_super_admin = request.user.role == 'super_admin'

    # Tenant isolation (super admin can access all)
    if not is_super_admin and task.tenant != request.user.tenant:
        return Response({"message": "Forbidden"}, status=403)

    # Permission: Only admin can fully edit tasks (title, description, assignee, etc.)
    # Regular users can only update status via PATCH endpoint
    if request.user.role != 'tenant_admin':
        return Response(
            {"message": "Only admin can edit task details"},
            status=403
        )

    serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)

    assigned_user = serializer.validated_data.get('assigned_to')
    if assigned_user and assigned_user.tenant != request.user.tenant:
        return Response(
            {"message": "Assigned user must belong to same tenant"},
            status=400
        )

    serializer.save()

    return Response({
        "success": True,
        "message": "Task updated successfully",
        "data": TaskListSerializer(task).data
    })


# API 20: Delete Task
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    is_super_admin = request.user.role == 'super_admin'

    # Tenant isolation (super admin can access all)
    if not is_super_admin and task.tenant != request.user.tenant:
        return Response({"message": "Forbidden"}, status=403)

    # Permission: Only admin can delete tasks
    if request.user.role != 'tenant_admin':
        return Response(
            {"message": "Only admin can delete tasks"},
            status=403
        )

    task_id_str = str(task.id)
    task.delete()

    return Response({
        "success": True,
        "message": "Task deleted successfully"
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_tasks(request):
    user = request.user
    is_super_admin = user.role == 'super_admin'
    
    # Super admin sees ALL tasks across all tenants
    if is_super_admin:
        qs = Task.objects.all()
    else:
        qs = Task.objects.filter(
            tenant=user.tenant,
            assigned_to=user
        )

    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)

    qs = qs.order_by('-priority', 'due_date')

    return Response({
        "success": True,
        "data": TaskListSerializer(qs, many=True).data
    })

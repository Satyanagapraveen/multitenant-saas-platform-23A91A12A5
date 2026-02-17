from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from projects.models import Project
from projects.serializers import (
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def projects_list_create(request):
    user = request.user
    tenant = user.tenant
    is_super_admin = user.role == 'super_admin'

    # ================= CREATE PROJECT =================
    if request.method == 'POST':
        # Super admin cannot create projects (no tenant)
        if is_super_admin:
            return Response(
                {"message": "Super admin cannot create projects"},
                status=403
            )
        if Project.objects.filter(tenant=tenant).count() >= tenant.max_projects:
            return Response(
                {"message": "Project limit reached"},
                status=403
            )

        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.save(
            tenant=tenant,
            created_by=request.user
        )

        return Response({
            "success": True,
            "data": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "createdBy": project.created_by.id,
                "createdAt": project.created_at
            }
        }, status=201)

    # ================= LIST PROJECTS =================
    # Super admin sees ALL projects across all tenants
    if is_super_admin:
        projects = Project.objects.all().annotate(
            task_count=Count('tasks'),
            completed_task_count=Count(
                'tasks',
                filter=Q(tasks__status='completed')
            )
        ).order_by('-created_at')
    else:
        projects = Project.objects.filter(tenant=tenant).annotate(
        task_count=Count('tasks'),
        completed_task_count=Count(
            'tasks',
            filter=Q(tasks__status='completed')
        )
        ).order_by('-created_at')

    serializer = ProjectListSerializer(projects, many=True)

    return Response({
        "success": True,
        "data": {
            "projects": serializer.data,
            "total": projects.count()
        }
    })




@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_or_delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    is_super_admin = request.user.role == 'super_admin'

    # Tenant isolation (super admin can access all)
    if not is_super_admin and project.tenant != request.user.tenant:
        return Response({"message": "Forbidden"}, status=403)

    # ================= GET PROJECT DETAILS =================
    if request.method == 'GET':
        return Response({
            "success": True,
            "data": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "createdBy": str(project.created_by.id) if project.created_by else None,
                "createdAt": project.created_at,
                "updatedAt": project.updated_at
            }
        })

    # Authorization (for PUT/DELETE only)
    if request.user.role != 'tenant_admin' and project.created_by != request.user:
        return Response({"message": "Not authorized"}, status=403)

    if request.method == 'PUT':
        serializer = ProjectUpdateSerializer(
            project,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Project updated successfully",
            "data": serializer.data
        })

    if request.method == 'DELETE':
        project.delete()
        return Response({
            "success": True,
            "message": "Project deleted successfully"
        })

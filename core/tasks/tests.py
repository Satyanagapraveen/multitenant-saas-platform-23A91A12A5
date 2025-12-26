"""Tests for tasks app."""
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from tenants.models import Tenant
from projects.models import Project
from tasks.models import Task


class TaskModelTests(TestCase):
    """Test cases for Task model"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Company",
            subdomain="test",
            status="active"
        )
        self.user = User.objects.create_user(
            email="user@test.com",
            password="Test@123",
            full_name="Test User",
            tenant=self.tenant
        )
        self.project = Project.objects.create(
            name="Test Project",
            tenant=self.tenant,
            created_by=self.user
        )
    
    def test_create_task(self):
        """Test creating a task"""
        task = Task.objects.create(
            title="Test Task",
            description="Task description",
            project=self.project,
            tenant=self.tenant,
            assigned_to=self.user,
            priority="medium"
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, "todo")
        self.assertEqual(task.priority, "medium")
    
    def test_task_status_choices(self):
        """Test task status values"""
        task = Task.objects.create(
            title="Test Task",
            project=self.project,
            tenant=self.tenant
        )
        # Default status is todo
        self.assertEqual(task.status, "todo")
        
        # Update to in_progress
        task.status = "in_progress"
        task.save()
        self.assertEqual(task.status, "in_progress")


class TaskAPITests(APITestCase):
    """Test cases for Task API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(
            name="Demo Company",
            subdomain="demo",
            status="active"
        )
        self.admin = User.objects.create_user(
            email="admin@demo.com",
            password="Admin@123",
            full_name="Admin User",
            tenant=self.tenant,
            role="tenant_admin"
        )
        self.project = Project.objects.create(
            name="Test Project",
            tenant=self.tenant,
            created_by=self.admin
        )
        # Login and get token
        response = self.client.post('/api/auth/login', {
            'email': 'admin@demo.com',
            'password': 'Admin@123',
            'tenantSubdomain': 'demo'
        }, format='json')
        self.token = response.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_task(self):
        """Test creating a task via API - tasks are created under projects"""
        response = self.client.post(f'/api/projects/{self.project.id}/tasks', {
            'title': 'New Task',
            'description': 'Task description',
            'priority': 'high'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_task_status(self):
        """Test updating task status (Kanban)"""
        task = Task.objects.create(
            title="Test Task",
            project=self.project,
            tenant=self.tenant,
            status="todo"
        )
        response = self.client.patch(f'/api/tasks/{task.id}/status', {
            'status': 'in_progress'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'in_progress')
    
    def test_list_tasks_by_project(self):
        """Test filtering tasks by project"""
        Task.objects.create(
            title="Task 1",
            project=self.project,
            tenant=self.tenant
        )
        response = self.client.get(f'/api/tasks?project={self.project.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

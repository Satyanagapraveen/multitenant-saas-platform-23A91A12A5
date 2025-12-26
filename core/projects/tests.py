"""Tests for projects app."""
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from tenants.models import Tenant
from projects.models import Project


class ProjectModelTests(TestCase):
    """Test cases for Project model"""
    
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
    
    def test_create_project(self):
        """Test creating a project"""
        project = Project.objects.create(
            name="Test Project",
            description="Test description",
            tenant=self.tenant,
            created_by=self.user
        )
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.status, "active")
        self.assertEqual(project.tenant, self.tenant)
    
    def test_project_str_representation(self):
        """Test project string representation"""
        project = Project.objects.create(
            name="Test Project",
            tenant=self.tenant,
            created_by=self.user
        )
        self.assertEqual(str(project), "Test Project")


class ProjectAPITests(APITestCase):
    """Test cases for Project API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(
            name="Demo Company",
            subdomain="demo",
            status="active",
            max_projects=10
        )
        self.admin = User.objects.create_user(
            email="admin@demo.com",
            password="Admin@123",
            full_name="Admin User",
            tenant=self.tenant,
            role="tenant_admin"
        )
        # Login and get token
        response = self.client.post('/api/auth/login', {
            'email': 'admin@demo.com',
            'password': 'Admin@123',
            'tenantSubdomain': 'demo'
        }, format='json')
        self.token = response.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_list_projects(self):
        """Test listing projects"""
        Project.objects.create(
            name="Project 1",
            tenant=self.tenant,
            created_by=self.admin
        )
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_project(self):
        """Test creating a project via API"""
        response = self.client.post('/api/projects', {
            'name': 'New Project',
            'description': 'Project description'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(name='New Project').exists())
    
    def test_project_tenant_isolation(self):
        """Test that users can only see their tenant's projects"""
        # Create another tenant with a project
        other_tenant = Tenant.objects.create(
            name="Other Company",
            subdomain="other",
            status="active"
        )
        other_user = User.objects.create_user(
            email="user@other.com",
            password="Test@123",
            full_name="Other User",
            tenant=other_tenant,
            role="user"
        )
        Project.objects.create(
            name="Other Project",
            tenant=other_tenant,
            created_by=other_user
        )
        
        # Current user should not see other tenant's project
        response = self.client.get('/api/projects')
        # Response format: {"success": true, "data": {"projects": [...], "total": N}}
        projects = response.data.get('data', {}).get('projects', [])
        project_names = [p.get('name') for p in projects]
        self.assertNotIn('Other Project', project_names)

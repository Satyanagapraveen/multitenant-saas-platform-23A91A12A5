"""
Tests for accounts app.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from tenants.models import Tenant


class UserModelTests(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Company",
            subdomain="test",
            status="active"
        )
    
    def test_create_user_with_email(self):
        """Test creating a user with email"""
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123",
            full_name="Test User",
            tenant=self.tenant,
            role="user"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("TestPass123"))
        self.assertEqual(user.role, "user")
    
    def test_create_superadmin_without_tenant(self):
        """Test super admin can be created without tenant"""
        user = User.objects.create_user(
            email="admin@system.com",
            password="Admin123",
            full_name="Super Admin",
            role="super_admin",
            tenant=None
        )
        self.assertIsNone(user.tenant)
        self.assertEqual(user.role, "super_admin")
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123",
            full_name="Test User",
            tenant=self.tenant
        )
        self.assertEqual(str(user), "test@example.com")


class AuthenticationTests(APITestCase):
    """Test cases for authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(
            name="Demo Company",
            subdomain="demo",
            status="active"
        )
        self.user = User.objects.create_user(
            email="user@demo.com",
            password="User@123",
            full_name="Demo User",
            tenant=self.tenant,
            role="user"
        )
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/api/auth/login', {
            'email': 'user@demo.com',
            'password': 'User@123',
            'tenantSubdomain': 'demo'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data.get('data', {}))
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = self.client.post('/api/auth/login', {
            'email': 'user@demo.com',
            'password': 'WrongPassword',
            'tenantSubdomain': 'demo'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_wrong_subdomain(self):
        """Test login with wrong subdomain - returns 404 for non-existent tenant"""
        response = self.client.post('/api/auth/login', {
            'email': 'user@demo.com',
            'password': 'User@123',
            'tenantSubdomain': 'wrongsubdomain'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_register_tenant(self):
        """Test tenant registration"""
        response = self.client.post('/api/auth/register-tenant', {
            'tenantName': 'New Company',
            'subdomain': 'newcompany',
            'adminFullName': 'Admin User',
            'adminEmail': 'admin@newcompany.com',
            'adminPassword': 'SecurePass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tenant.objects.filter(subdomain='newcompany').exists())
    
    def test_register_duplicate_subdomain(self):
        """Test registration with existing subdomain fails"""
        response = self.client.post('/api/auth/register-tenant', {
            'tenantName': 'Another Company',
            'subdomain': 'demo',  # Already exists
            'fullName': 'Admin User',
            'email': 'admin@another.com',
            'password': 'SecurePass123'
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT])


class ProtectedEndpointTests(APITestCase):
    """Test cases for protected endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(
            name="Demo Company",
            subdomain="demo",
            status="active"
        )
        self.user = User.objects.create_user(
            email="user@demo.com",
            password="User@123",
            full_name="Demo User",
            tenant=self.tenant,
            role="user"
        )
    
    def test_me_endpoint_without_auth(self):
        """Test /me endpoint without authentication"""
        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_me_endpoint_with_auth(self):
        """Test /me endpoint with authentication"""
        # Login first
        login_response = self.client.post('/api/auth/login', {
            'email': 'user@demo.com',
            'password': 'User@123',
            'tenantSubdomain': 'demo'
        }, format='json')
        token = login_response.data['data']['token']
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], 'user@demo.com')

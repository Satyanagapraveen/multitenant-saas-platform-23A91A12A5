"""
Django management command to seed the database with demo data.

Creates:
- 1 Super Admin (superadmin@system.com / Admin@123)
- 1 Demo Tenant (Demo Company, subdomain: demo)
- 1 Tenant Admin (admin@demo.com / Demo@123)
- 2 Regular Users (user1@demo.com, user2@demo.com / User@123)
- 2 Sample Projects
- 5 Sample Tasks
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from tenants.models import Tenant
from accounts.models import User
from projects.models import Project
from tasks.models import Task


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Task.objects.all().delete()
            Project.objects.all().delete()
            User.objects.all().delete()
            Tenant.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared!'))

        with transaction.atomic():
            # 1. Create Super Admin (no tenant)
            super_admin, created = User.objects.get_or_create(
                email='superadmin@system.com',
                defaults={
                    'full_name': 'Super Admin',
                    'role': 'super_admin',
                    'is_active': True,
                    'is_staff': True,
                    'is_superuser': True,
                    'tenant': None
                }
            )
            if created:
                super_admin.set_password('Admin@123')
                super_admin.save()
                self.stdout.write(self.style.SUCCESS('✓ Super Admin created'))
            else:
                # Ensure existing superadmin has correct flags
                super_admin.is_staff = True
                super_admin.is_superuser = True
                super_admin.save()
                self.stdout.write('  Super Admin already exists (flags updated)')

            # 2. Create Demo Tenant
            demo_tenant, created = Tenant.objects.get_or_create(
                subdomain='demo',
                defaults={
                    'name': 'Demo Company',
                    'status': 'active',
                    'subscription_plan': 'pro',
                    'max_users': 20,
                    'max_projects': 20
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Demo Tenant created'))
            else:
                self.stdout.write('  Demo Tenant already exists')

            # 3. Create Tenant Admin for Demo Company
            tenant_admin, created = User.objects.get_or_create(
                email='admin@demo.com',
                tenant=demo_tenant,
                defaults={
                    'full_name': 'Demo Admin',
                    'role': 'tenant_admin',
                    'is_active': True
                }
            )
            if created:
                tenant_admin.set_password('Demo@123')
                tenant_admin.save()
                self.stdout.write(self.style.SUCCESS('✓ Tenant Admin created'))
            else:
                self.stdout.write('  Tenant Admin already exists')

            # 4. Create Regular Users
            user1, created = User.objects.get_or_create(
                email='user1@demo.com',
                tenant=demo_tenant,
                defaults={
                    'full_name': 'John Doe',
                    'role': 'user',
                    'is_active': True
                }
            )
            if created:
                user1.set_password('User@123')
                user1.save()
                self.stdout.write(self.style.SUCCESS('✓ User 1 (John Doe) created'))
            else:
                self.stdout.write('  User 1 already exists')

            user2, created = User.objects.get_or_create(
                email='user2@demo.com',
                tenant=demo_tenant,
                defaults={
                    'full_name': 'Jane Smith',
                    'role': 'user',
                    'is_active': True
                }
            )
            if created:
                user2.set_password('User@123')
                user2.save()
                self.stdout.write(self.style.SUCCESS('✓ User 2 (Jane Smith) created'))
            else:
                self.stdout.write('  User 2 already exists')

            # 5. Create Sample Projects
            project1, created = Project.objects.get_or_create(
                name='Website Redesign',
                tenant=demo_tenant,
                defaults={
                    'description': 'Complete redesign of the company website with modern UI/UX',
                    'status': 'active',
                    'created_by': tenant_admin
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Project 1 (Website Redesign) created'))
            else:
                self.stdout.write('  Project 1 already exists')

            project2, created = Project.objects.get_or_create(
                name='Mobile App Development',
                tenant=demo_tenant,
                defaults={
                    'description': 'Build a cross-platform mobile app for customers',
                    'status': 'active',
                    'created_by': tenant_admin
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Project 2 (Mobile App Development) created'))
            else:
                self.stdout.write('  Project 2 already exists')

            # 6. Create Sample Tasks
            tasks_data = [
                {
                    'title': 'Design homepage mockup',
                    'description': 'Create high-fidelity mockup for the new homepage',
                    'project': project1,
                    'status': 'in_progress',
                    'priority': 'high',
                    'assigned_to': user1,
                    'due_date': date.today() + timedelta(days=7)
                },
                {
                    'title': 'Implement responsive navigation',
                    'description': 'Build responsive navigation component with mobile menu',
                    'project': project1,
                    'status': 'todo',
                    'priority': 'medium',
                    'assigned_to': user2,
                    'due_date': date.today() + timedelta(days=14)
                },
                {
                    'title': 'Set up CI/CD pipeline',
                    'description': 'Configure GitHub Actions for automated deployment',
                    'project': project1,
                    'status': 'completed',
                    'priority': 'high',
                    'assigned_to': user1,
                    'due_date': date.today() - timedelta(days=2)
                },
                {
                    'title': 'Design app screens',
                    'description': 'Create UI designs for all main app screens',
                    'project': project2,
                    'status': 'in_progress',
                    'priority': 'high',
                    'assigned_to': user1,
                    'due_date': date.today() + timedelta(days=10)
                },
                {
                    'title': 'Set up React Native project',
                    'description': 'Initialize React Native project with navigation and state management',
                    'project': project2,
                    'status': 'todo',
                    'priority': 'medium',
                    'assigned_to': user2,
                    'due_date': date.today() + timedelta(days=5)
                }
            ]

            tasks_created = 0
            for task_data in tasks_data:
                task, created = Task.objects.get_or_create(
                    title=task_data['title'],
                    project=task_data['project'],
                    tenant=demo_tenant,
                    defaults={
                        'description': task_data['description'],
                        'status': task_data['status'],
                        'priority': task_data['priority'],
                        'assigned_to': task_data['assigned_to'],
                        'due_date': task_data['due_date']
                    }
                )
                if created:
                    tasks_created += 1

            if tasks_created > 0:
                self.stdout.write(self.style.SUCCESS(f'✓ {tasks_created} Tasks created'))
            else:
                self.stdout.write('  Tasks already exist')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('Login Credentials:')
        self.stdout.write('-' * 30)
        self.stdout.write('Super Admin:')
        self.stdout.write('  Email: superadmin@system.com')
        self.stdout.write('  Password: Admin@123')
        self.stdout.write('')
        self.stdout.write('Tenant Admin (Demo Company):')
        self.stdout.write('  Subdomain: demo')
        self.stdout.write('  Email: admin@demo.com')
        self.stdout.write('  Password: Demo@123')
        self.stdout.write('')
        self.stdout.write('Regular Users (Demo Company):')
        self.stdout.write('  Subdomain: demo')
        self.stdout.write('  Email: user1@demo.com / Password: User@123')
        self.stdout.write('  Email: user2@demo.com / Password: User@123')

#!/bin/bash
set -e

echo "=== Multi-Tenant SaaS Backend Startup ==="

# Wait for database to be ready
echo "Waiting for database..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Database not ready, waiting 2 seconds..."
  sleep 2
done

echo "✓ Database is ready!"


# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput
echo "✓ Migrations complete!"

# Load seed data
echo "Loading seed data..."
python manage.py seed_data || echo "Seed data already exists, skipping"

echo "✓ Seed data loaded!"

# Verify seed data
echo "Verifying seed data..."
python -c "
from django.conf import settings
import django
django.setup()

from accounts.models import User
from tenants.models import Tenant
from projects.models import Project
from tasks.models import Task

# Check counts
users = User.objects.count()
tenants = Tenant.objects.count()
projects = Project.objects.count()
tasks = Task.objects.count()

# Check super admin exists
super_admin = User.objects.filter(email='superadmin@system.com', role='super_admin').exists()

print(f'  Users: {users}')
print(f'  Tenants: {tenants}')
print(f'  Projects: {projects}')
print(f'  Tasks: {tasks}')
print(f'  Super Admin exists: {super_admin}')

if not super_admin:
    print('ERROR: Super admin not found!')
    exit(1)
"
echo "✓ Seed data verified!"

# Start server
echo "Starting Django server on 0.0.0.0:5000..."
exec python manage.py runserver 0.0.0.0:5000

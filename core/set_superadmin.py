import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
import django
django.setup()
from accounts.models import User
u=User.objects.filter(email='superadmin@system.com').first()
print('Before:', u.email if u else None, getattr(u,'is_staff',None), getattr(u,'is_superuser',None))
if u:
    u.is_staff=True
    u.is_superuser=True
    u.save()
    print('After:', u.email, u.is_staff, u.is_superuser)
else:
    print('No superadmin user found')

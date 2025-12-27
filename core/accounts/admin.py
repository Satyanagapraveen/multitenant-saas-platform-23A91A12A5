from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ('email','full_name','role','is_staff','is_superuser')
    ordering = ('email',)
    fieldsets = (
    (None, {'fields': ('email','password')}),
    ('Personal info', {'fields': ('full_name','role','tenant')}),
    ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
    )
    add_fieldsets = (
    (None, {
    'classes': ('wide',),
    'fields': ('email','full_name','password1','password2'),
    }),
    )
    search_fields = ('email','full_name')

   
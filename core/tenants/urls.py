from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_tenants, name='list_tenants'),
    path('<uuid:tenant_id>', views.tenant_detail, name='tenant_detail'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_audit_logs, name='list_audit_logs'),
    path('<uuid:log_id>', views.get_audit_log, name='get_audit_log'),
]

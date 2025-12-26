from django.urls import path
from tasks.views import my_tasks, project_tasks, update_task_status, update_task, delete_task

urlpatterns = [
    path('projects/<uuid:project_id>/tasks', project_tasks),
    path('tasks/<uuid:task_id>/status', update_task_status),
    path('tasks/<uuid:task_id>', update_task),
    path('tasks/<uuid:task_id>/delete', delete_task),
    path('tasks', my_tasks),
]

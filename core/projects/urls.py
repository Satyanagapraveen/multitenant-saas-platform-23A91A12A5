from django.urls import path
from projects.views import projects_list_create,update_or_delete_project

urlpatterns = [
    path('projects', projects_list_create),                 # GET + POST
    path('projects/<uuid:project_id>',update_or_delete_project),  # PUT + DELETE
]

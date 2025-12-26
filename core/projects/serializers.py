from rest_framework import serializers
from projects.models import Project

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status']


class ProjectListSerializer(serializers.ModelSerializer):
    task_count = serializers.IntegerField(read_only=True)
    completed_task_count = serializers.IntegerField(read_only=True)
    created_by = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status',
            'created_by', 'task_count', 'completed_task_count', 'created_at'
        ]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status']

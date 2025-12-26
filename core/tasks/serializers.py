from rest_framework import serializers
from tasks.models import Task

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'assigned_to', 'due_date']


class TaskListSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assigned_to', 'due_date', 'created_at'
        ]

    def get_assigned_to(self, obj):
        if obj.assigned_to:
            return {
                "id": obj.assigned_to.id,
                "full_name": obj.assigned_to.full_name,
                "email": obj.assigned_to.email
            }
        return None


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status',
            'priority', 'assigned_to', 'due_date'
        ]

from rest_framework import serializers

from project.models import Project
from .models import Ticket, Status


class TicketSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    labels_names = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'key', 'title', 'description', 'category', 'priority', 'type',
            'summary', 'suggested_solution', 'is_active',
            'project', 'project_name', 'status', 'status_name',
            'assigned_to', 'assigned_to_username', 'due_date', 'created_by', 'created_by_username',
            'labels_names', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_labels_names(self, obj):
        return list(obj.labels.values_list('name', flat=True))
    

class DueTicketSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()



class CreateTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            "key",
            "title",
            "description",
            "category",
            "priority",
            "type",
            "summary",
            "suggested_solution",
            "due_date",
            "created_by"
        ]
        extra_kwargs = {
            'created_by': {'read_only': True}
        }


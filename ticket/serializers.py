from rest_framework import serializers

from project.models import Project
from .models import Ticket, Status, Label
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    avatar = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'avatar']
    
    def get_avatar(self, obj):
        if obj.first_name and obj.last_name:
            initials = f"{obj.first_name[0]}{obj.last_name[0]}".upper()
            return f"{initials}"

class TicketSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    assigned_to = UserSerializer(read_only=True)
    created_by = serializers.StringRelatedField()
    tickets_count = serializers.IntegerField(read_only=True)
    

    class Meta:
        model = Ticket
        fields = [
            'id', 'key', 'title', 'description', 'category', 'priority', 'type',
            'summary', 'suggested_solution', 'is_active',
            'project', 'status',
            'assigned_to', 'due_date', 'created_by',
            'created_at', 'updated_at', 'tickets_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_labels(self, obj):
        return list(obj.labels.values_list('name', flat=True))
    

    
    
    
class BacklogTicketsSerializer(serializers.ModelSerializer):
    
    assigned_to = UserSerializer(read_only=True)
    status = serializers.StringRelatedField()
    
    class Meta:
        model = Ticket
        fields = ['id', 'key', 'title', 'priority', 'type', 'status', 'assigned_to']
    

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
            "status",
            "summary",
            "suggested_solution",
            "due_date",
            "created_by"
        ]
        extra_kwargs = {
            'created_by': {'read_only': True}
        }
        

class TicketsByStatusListSerializer(serializers.ModelSerializer):
    
    tickets = TicketSerializer(many=True, read_only=True)
    class Meta:
        model = Status
        fields = ['id', 'name', 'order','tickets']
        
        
        
        

class AssignTicketSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Ticket
        fields = ['assigned_to']

    def validate_assigned_to(self, value):
        project = self.context['project']

        if value and not project.members.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "Usuario no pertenece al proyecto"
            )

        return value


class UpdateTicketSerializer(serializers.ModelSerializer):

    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Ticket
        fields = [
            'title', 'key','description', 'category', 'priority', 'type',
            'summary', 'suggested_solution', 'status',
            'due_date'
        ]


    def validate_status(self, value):
        project = self.context.get('project')
        if value and project and value.project_id != project.id:
            raise serializers.ValidationError("El estado no pertenece a este proyecto")
        return value




class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name', 'color']
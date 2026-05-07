
from rest_framework import serializers
from project.models import Sprint
from django.conf import settings
from ticket.models import Ticket
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
        
        
        
class TicketsSerializer(serializers.ModelSerializer):
    
    assigned_to = UserSerializer(read_only=True)
    status = serializers.StringRelatedField()
    class Meta:
        model = Ticket
        fields = ['id', 'key', 'title', 'priority', 'type', 'status', 'assigned_to']



class SprintListSerializer(serializers.ModelSerializer):
    
    project = serializers.StringRelatedField()
    tickets = TicketsSerializer(many=True, read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Sprint
        fields = ['id', 'name', 'status', 'start_date', 'end_date', 'is_active', 'project', 'ticket_count', "tickets"]


class SprintCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Sprint
        fields = ['name', 'start_date', 'end_date', 'status']
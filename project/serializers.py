from rest_framework import serializers

from ticket.models import Status
from .models import Project, ProjectMember
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'avatar']
        
    
    def get_avatar(self, obj):
        if obj.first_name and obj.last_name:
            initials = f"{obj.first_name[0]}{obj.last_name[0]}".upper()
            return f"{initials}"
        
        
class ProjectListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members_count = serializers.IntegerField(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    sprints = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'key','created_by', 'created_at', 'members_count', 'members', 'sprints']
        read_only_fields = ['id', 'created_at']



    
class StatusSerializer(serializers.ModelSerializer):
    
    total_tickets = serializers.IntegerField(read_only=True)
    class Meta:
        model = Status
        fields = ['id', 'name', 'total_tickets']  
    

class StatusProjectSerializer(serializers.ModelSerializer):
    
    tickets_count = serializers.IntegerField(read_only=True)
    sprints_count = serializers.IntegerField(read_only=True)
    statuses = StatusSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'tickets_count', 'sprints_count', 'statuses']
        read_only_fields = ['id']




class ActivitySerializer(serializers.Serializer):
    action = serializers.CharField()
    user = UserSerializer(read_only=True)
    timestamp = serializers.DateTimeField()




class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'role', 'user', 'project']
        


class ProjectMemberCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectMember
        fields = ['role', 'user']



class CreateProjectSerializer(serializers.ModelSerializer):
    
    members = serializers.ListField(child=serializers.IntegerField(), required=False)
    
    class Meta:
        model = Project
        fields = ['key', 'name', 'description', 'members']
        
    
    def create(self, validated_data):
        
        members_ids = validated_data.pop('members', [])
        user = self.context['request'].user

        project = Project.objects.create(
            created_by=user,
            **validated_data
        )

        ProjectMember.objects.create(
            user=user,
            project=project,
            role='admin'
        )

        for user_id in members_ids:
            if user_id != user.id:
                if User.objects.filter(id=user_id).exists(): 
                    ProjectMember.objects.create(
                        user_id=user_id,
                        project=project,
                        role='developer'
                    )

        return project

class UpdateProjectSerializer(serializers.ModelSerializer):
    
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['key', 'name', 'description']
        
    





class DashboardCardsSerializer(serializers.Serializer):
    
    project_count = serializers.IntegerField(read_only=True)
    my_tickets_count = serializers.IntegerField(read_only=True)
    tickets_count = serializers.IntegerField(read_only=True)
    unassigned_tickets_count = serializers.IntegerField(read_only=True)
    


class StatusCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = ['name', 'order']



class StatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = ['name']
    



class ProjectActiveSerializer(serializers.ModelSerializer):
    
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'members']
 



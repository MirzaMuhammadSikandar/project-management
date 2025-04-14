from rest_framework import serializers
from .models import User, Project, Task, Document, Comment, TimelineEvent, Notification
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings

# ------------------- USER ------------------------- 
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'is_staff', 'password']
        read_only_fields = ['id', 'is_staff', 'is_active']

    def validate_role(self, value):
        allowed_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if value not in allowed_roles:
            raise serializers.ValidationError("Invalid role")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
# ------------------- TOKEN ------------------------- 
class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        data['role'] = self.user.role
        return data
    
# ------------------- PROJECT ------------------------- 
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ------------------- TASK ------------------------- 
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'project', 'title', 'description', 'is_completed', 'assigned_to', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# ------------------- DOCUMENT ------------------------- 
class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'project', 'uploaded_by', 'file', 'file_url', 'name', 'description', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'file_url']

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError("You must upload a file.")
        return value

    def get_file_url(self, obj):
        if not obj.file:
            return None
        return f"{settings.MEDIA_HOST}{obj.file.url}"

# ------------------- COMMENT ------------------------- 
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'project', 'task', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, data):
        if self.instance:
            # Use existing instance values if not provided again
            project = data.get("project", self.instance.project)
            task = data.get("task", self.instance.task)
        else:
            project = data.get("project")
            task = data.get("task")

        if not project and not task:
            raise serializers.ValidationError("Comment must be linked to either a project or a task.")
        
        return data
    
# ------------------- TIMELINE ------------------------- 
class TimelineEventSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = TimelineEvent
        fields = ['id', 'project', 'user', 'event_type', 'description', 'created_at']

# ------------------- NOTIFICATION -------------------------   
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']

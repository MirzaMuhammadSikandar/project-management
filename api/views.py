from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserSerializer, TokenSerializer, ProjectSerializer, TaskSerializer, DocumentSerializer, CommentSerializer, TimelineEventSerializer, NotificationSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions
from .models import Project, Task, Document, Comment, TimelineEvent, Notification
from django.contrib.auth import get_user_model
from .utils import log_event

# ------------------- USER View ------------------------- 
class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            serializer = TokenSerializer(data={"email": email, "password": password})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        

# ------------------- PROJECT View ------------------------- 
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        log_event( 
            project,
            self.request.user,
            "project_created",
            f"Project '{project.name}' was created"
        )


# ------------------- TASK View ------------------------- 
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user)

    def perform_create(self, serializer):
        task = serializer.save()
        log_event(  
            task.project,
            self.request.user,
            "task_created",
            f"Task '{task.title}' was created"
        )

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        try:
            task = self.get_object()
            user_id = request.data.get("user_id")
            if not user_id:
                return Response({"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            User = get_user_model()
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            task.assigned_to = user
            task.save()

            log_event(  
                task.project,
                self.request.user,
                "task_updated",
                f"Task '{task.title}' was assigned to {user.email}"
            )

            return Response({"detail": "Task assigned successfully"}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        

# ------------------- DOCUMENT View ------------------------- 
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(project__owner=self.request.user)

    def perform_create(self, serializer):
        doc = serializer.save(uploaded_by=self.request.user)
        log_event( 
            doc.project,
            self.request.user,
            "document_uploaded",
            f"Document '{doc.name}' uploaded"
        )

# ------------------- COMMENT View ------------------------- 
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.request.query_params.get('task')
        project_id = self.request.query_params.get('project')
        queryset = Comment.objects.all()

        if task_id:
            queryset = queryset.filter(task__id=task_id)
        if project_id:
            queryset = queryset.filter(project__id=project_id)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        project = comment.project or comment.task.project
        log_event(  
            project,
            self.request.user,
            "comment_added",
            f"Comment added: '{comment.content[:50]}'"
        )

# ------------------- TIMELINE View ------------------------- 
class TimelineViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TimelineEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.request.query_params.get("project")
        if not project_id:
            return TimelineEvent.objects.none()
        
        return TimelineEvent.objects.filter(project__id=project_id).order_by('-created_at')

# ------------------- NOTIFICATION View ------------------------- 
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
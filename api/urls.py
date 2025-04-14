from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ProjectViewSet, TaskViewSet, DocumentViewSet, CommentViewSet, TimelineViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'timeline', TimelineViewSet, basename='timeline')

urlpatterns = [
    path('api/', include(router.urls)),  
]

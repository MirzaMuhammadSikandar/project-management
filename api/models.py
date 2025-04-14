from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings

# ------------------- USER Manager -------------------------
class UserManager(BaseUserManager):
     def create_user(self, email, password=None, role="project_manager", **extra_fields):
         if not email:
             raise ValueError("Email is required")
         email = self.normalize_email(email)
         user = self.model(email=email, role=role, **extra_fields)
         user.set_password(password)
         user.save(using=self._db)
         return user
 
     def create_superuser(self, email, password=None, **extra_fields):
         extra_fields.setdefault("is_staff", True)
         extra_fields.setdefault("is_superuser", True)
         return self.create_user(email, password, role="project_manager", **extra_fields)

# ------------------- USER Model -------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ("project_manager", "Project Manager"),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default="project_manager")
    email = models.EmailField(unique=True)

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [] 

    objects = UserManager()

    def __str__(self):
        return self.email
    
# ------------------- PROJECT Model -------------------------
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")

    def __str__(self):
        return self.name

# ------------------- TASK Model -------------------------
class Task(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
# ------------------- DOCUMENT Model -------------------------    
class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
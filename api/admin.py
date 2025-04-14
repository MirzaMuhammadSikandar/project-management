# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Task, Document, Comment

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'role', 'is_staff', 'is_active', 'last_login']
    search_fields = ['email']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Comment)

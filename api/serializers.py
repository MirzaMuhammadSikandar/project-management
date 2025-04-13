from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
    
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
    
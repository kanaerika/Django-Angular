from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Role, Profile

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProfileSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'user_full_name', 'user_email', 'phone','bio', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'user']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id',  'email', 'first_name', 'last_name','full_name','role_name',  
                    'profile', 'date_joined', 'last_login', 'is_active']
        read_only_fields = ['date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role', required=False, allow_null=True)
    admin_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    ADMIN_SECRET_CODE = "CMR-ADMIN-2026"  # code secret requis pour créer un compte Admin

    class Meta:
        model = CustomUser
        fields = ['first_name', 'username', 'last_name', 'email', 'role_id', 'password', 'confirm_password', 'admin_code']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})

        role = attrs.get('role')
        admin_code = attrs.pop('admin_code', '')
        if role and role.name.lower() == 'admin':
            if admin_code != self.ADMIN_SECRET_CODE:
                raise serializers.ValidationError({"admin_code": "Code administrateur invalide."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        # Les admins du système sont aussi "staff" Django (requis par IsAdminUser)
        if user.role and user.role.name.lower() == 'admin':
            user.is_staff = True
            user.save(update_fields=['is_staff'])
        # Créer automatiquement un profil pour l'utilisateur
        Profile.objects.create(user=user)
        return user



class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Nom d'utilisateur ou mot de passe incorrect.")
        
        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé.")
        
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_confirm_password']:
            raise serializers.ValidationError({"new_password": "Les nouveaux mots de passe ne correspondent pas."})
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone','bio']
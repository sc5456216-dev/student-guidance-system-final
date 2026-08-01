from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentProfile, MentorProfile, CounselorProfile

User = get_user_model()

class StudentProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'user_email', 'user_username', 'roll_number',
            'date_of_birth', 'phone_number', 'address', 
            'guardian_name', 'guardian_contact'
        ]
        read_only_fields = ['user']

class StudentProfileCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'username', 'email', 'password', 'roll_number',
            'date_of_birth', 'phone_number', 'address',
            'guardian_name', 'guardian_contact'
        ]
    
    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='student'
        )
        
        student = StudentProfile.objects.create(user=user, **validated_data)
        return student

class MentorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MentorProfile
        fields = [
            'id', 'user', 'user_email', 'user_username', 'employee_id',
            'specialization', 'max_students', 'is_active'
        ]
        read_only_fields = ['user']

class CounselorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CounselorProfile
        fields = [
            'id', 'user', 'user_email', 'user_username', 'employee_id',
            'designation', 'license_number', 'is_active'
        ]
        read_only_fields = ['user']
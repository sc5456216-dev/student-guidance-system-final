# students/serializers.py
from rest_framework import serializers
from .models import Student
from django.contrib.auth import get_user_model
from enrollment.models import Enrollment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'name', 'email', 'phone',
            'date_of_birth', 'address', 'student_id',
            'enrollment_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'student_id', 'enrollment_date']


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='batch.course.title', read_only=True)
    batch_name = serializers.CharField(source='batch.batch_name', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'batch', 'batch_name', 'course_title', 'status', 'payment_status', 'enrolled_at', 'grade']


# --- COMMENTED OUT: Serializers for missing apps ---
# class AppointmentSerializer(...): pass
# class AssessmentResultSerializer(...): pass
# class CounselingSessionSerializer(...): pass


class DashboardSerializer(serializers.Serializer):
    profile = StudentSerializer(read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    # upcoming_appointments = AppointmentSerializer(many=True, read_only=True)
    # recent_assessments = AssessmentResultSerializer(many=True, read_only=True)
    # counseling_sessions = CounselingSessionSerializer(many=True, read_only=True)
from rest_framework import serializers
from .models import Course, Batch, BatchEnrollment, MentorAssignment
from profiles.models import StudentProfile, MentorProfile
from profiles.serializers import StudentProfileSerializer, MentorProfileSerializer

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'code', 'title', 'description', 'credits', 'is_active']

class BatchSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    primary_mentor_name = serializers.CharField(
        source='primary_mentor.user.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = Batch
        fields = [
            'id', 'name', 'course', 'course_title', 'course_code',
            'start_date', 'end_date', 'primary_mentor', 
            'primary_mentor_name', 'is_active'
        ]

class BatchDetailSerializer(BatchSerializer):
    students = serializers.SerializerMethodField()
    assigned_mentors = serializers.SerializerMethodField()
    
    def get_students(self, obj):
        enrollments = obj.enrollments.filter(is_active=True)
        return StudentProfileSerializer(
            [e.student for e in enrollments], 
            many=True
        ).data
    
    def get_assigned_mentors(self, obj):
        assignments = obj.assigned_mentors.filter()
        return MentorProfileSerializer(
            [a.mentor for a in assignments], 
            many=True
        ).data
    
    class Meta(BatchSerializer.Meta):
        fields = BatchSerializer.Meta.fields + ['students', 'assigned_mentors']

class BatchEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.user.get_full_name', 
        read_only=True
    )
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    
    class Meta:
        model = BatchEnrollment
        fields = [
            'id', 'student', 'student_name', 'batch', 'batch_name',
            'enrolled_date', 'is_active'
        ]

class MentorAssignmentSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(
        source='mentor.user.get_full_name', 
        read_only=True
    )
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    
    class Meta:
        model = MentorAssignment
        fields = [
            'id', 'mentor', 'mentor_name', 'batch', 'batch_name',
            'assigned_date', 'is_primary'
        ]
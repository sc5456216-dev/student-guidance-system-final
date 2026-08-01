# course/serializers.py
from rest_framework import serializers
from .models import Course, CourseBatch

class CourseBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseBatch
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CourseWithBatchesSerializer(CourseSerializer):
    batches = CourseBatchSerializer(many=True, read_only=True)
    
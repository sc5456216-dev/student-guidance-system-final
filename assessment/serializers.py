from rest_framework import serializers
from .models import Question, AssessmentResult
from course.serializers import CourseSerializer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AssessmentResultSerializer(serializers.ModelSerializer):
    course_recommendations = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentResult
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
from rest_framework import serializers
from .models import CounselingSession
from authentication.serializers import UserSerializer
from assessment.serializers import AssessmentResultSerializer

class CounselingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselingSession
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CounselingSessionDetailSerializer(CounselingSessionSerializer):
    student = UserSerializer(read_only=True)
    counselor = UserSerializer(read_only=True)
    assessment_result = AssessmentResultSerializer(read_only=True)
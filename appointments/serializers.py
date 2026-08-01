# appointments/serializers.py
from rest_framework import serializers
from .models import Appointment
from authentication.serializers import UserSerializer
from course.serializers import CourseSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['student', 'created_at', 'updated_at', 'is_deleted']

    # No validate() method needed – the foreign keys are enough


class AppointmentDetailSerializer(AppointmentSerializer):
    # Note: student/advisor are not User, they are profile models.
    # You may need separate profile serializers later.
    student = UserSerializer(read_only=True)
    advisor = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
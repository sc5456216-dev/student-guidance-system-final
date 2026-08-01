from rest_framework import serializers
from .models import Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'batch', 'status', 'payment_status', 'enrolled_at', 'grade', 'feedback']
        read_only_fields = ['id', 'enrolled_at', 'student']   # student is read-only

    def validate(self, data):
        # Get the student from the request context (the logged‑in user)
        request = self.context.get('request')
        student = request.user if request else None

        # If no student in context, try data (fallback, but should not happen)
        if not student:
            student = data.get('student')

        batch = data.get('batch')
        if student and batch:
            if Enrollment.objects.filter(student=student, batch=batch, is_deleted=False).exists():
                raise serializers.ValidationError("Student is already enrolled in this batch.")
        return data
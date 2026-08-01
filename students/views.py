from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from .models import Student
from .serializers import StudentSerializer, DashboardSerializer
from enrollment.models import Enrollment

# --- COMMENTED OUT: Missing apps ---
# from appointments.models import Appointment
# from assessment.models import AssessmentResult
# from counseling.models import CounselingSession


# ---------- BASIC VIEWS ----------
def home(request):
    return JsonResponse({
        "message": "Welcome to the Student Guidance System API!",
        "status": "running"
    })


def cache_test_view(request):
    return JsonResponse({
        "cached_at": timezone.now().isoformat(),
        "message": "This response is cached for 15 minutes!"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_email_view(request):
    to_email = request.data.get('to_email')
    if not to_email:
        return Response({
            'status': 'error',
            'message': 'Please provide "to_email" in the request body'
        }, status=400)

    try:
        send_mail(
            'Test Email from Student Guidance System',
            f'Hello! This is a test email sent to {to_email}',
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
        return Response({
            'status': 'success',
            'message': f'Email sent to {to_email}'
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ---------- STUDENT PROFILE VIEW ----------
class StudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        student, created = Student.objects.get_or_create(user=self.request.user)
        return student


# ---------- DASHBOARD VIEW (SIMPLIFIED) ----------
class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Profile
        student, created = Student.objects.get_or_create(user=user)

        # Enrollments (only if model exists)
        enrollments = Enrollment.objects.filter(student=user, is_deleted=False)

        data = {
            'profile': student,
            'enrollments': enrollments,
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data)


# ---------- DASHBOARD HTML PAGE ----------
def dashboard_page(request):
    """Serve the student dashboard HTML page."""
    return render(request, 'students/dashboard.html')
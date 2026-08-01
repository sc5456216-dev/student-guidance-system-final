from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import StudentProfile, MentorProfile, CounselorProfile
from .serializers import (
    StudentProfileSerializer, StudentProfileCreateSerializer,
    MentorProfileSerializer, CounselorProfileSerializer
)
from authentication.permissions import IsStudent, IsAdvisor, IsStaffOrAdmin

# --- Student Registration (Public) ---
class StudentRegisterView(generics.CreateAPIView):
    serializer_class = StudentProfileCreateSerializer
    permission_classes = []  # Public registration
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            return Response({
                "message": "Student registered successfully!",
                "student_id": student.id,
                "username": student.user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- StudentProfile ViewSet (Authenticated users) ---
class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated(), IsStaffOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return StudentProfile.objects.filter(user=user)
        elif user.role in ['advisor', 'super_admin']:
            return StudentProfile.objects.all()
        return StudentProfile.objects.none()

# --- MentorProfile ViewSet ---
class MentorProfileViewSet(viewsets.ModelViewSet):
    queryset = MentorProfile.objects.all()
    serializer_class = MentorProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return MentorProfile.objects.all()
        elif user.role == 'advisor':
            # Counselors might need to see mentors for reference
            return MentorProfile.objects.filter(is_active=True)
        return MentorProfile.objects.none()

# --- CounselorProfile ViewSet ---
class CounselorProfileViewSet(viewsets.ModelViewSet):
    queryset = CounselorProfile.objects.all()
    serializer_class = CounselorProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return CounselorProfile.objects.all()
        elif user.role == 'advisor':
            return CounselorProfile.objects.filter(user=user)
        elif user.role == 'student':
            # Students might need to see counselors for appointments
            return CounselorProfile.objects.filter(is_active=True)
        return CounselorProfile.objects.none()
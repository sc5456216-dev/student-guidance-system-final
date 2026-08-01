from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Course, Batch, BatchEnrollment, MentorAssignment
from .serializers import (
    CourseSerializer, BatchSerializer, BatchDetailSerializer,
    BatchEnrollmentSerializer, MentorAssignmentSerializer
)
from authentication.permissions import IsStudent, IsAdvisor, IsStaffOrAdmin

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'code', 'description']
    ordering_fields = ['title', 'code', 'credits']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return [IsAuthenticated()]

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.filter(is_active=True)
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'course__title', 'course__code']
    ordering_fields = ['name', 'start_date', 'end_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BatchDetailSerializer
        return BatchSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'student':
            # Show batches the student is enrolled in
            student_profile = getattr(user, 'student_profile', None)
            if student_profile:
                enrolled_batch_ids = student_profile.enrollments.filter(
                    is_active=True
                ).values_list('batch_id', flat=True)
                return queryset.filter(id__in=enrolled_batch_ids)
        elif user.role == 'advisor':
            # Show batches where this counselor is the primary mentor or assigned
            counselor_profile = getattr(user, 'counselor_profile', None)
            if counselor_profile:
                mentor_profile = getattr(counselor_profile, 'mentor_profile', None)
                if mentor_profile:
                    assigned_batch_ids = mentor_profile.assigned_batches.filter(
                    ).values_list('batch_id', flat=True)
                    return queryset.filter(id__in=assigned_batch_ids)
        return queryset

class BatchEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = BatchEnrollment.objects.filter(is_active=True)
    serializer_class = BatchEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__username', 'batch__name']
    ordering_fields = ['enrolled_date']
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsStudent() | IsStaffOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        # If student is creating, force enrollment for themselves
        if self.request.user.role == 'student':
            student_profile = getattr(self.request.user, 'student_profile', None)
            if student_profile:
                serializer.save(student=student_profile)
            else:
                raise serializers.ValidationError(
                    "Student profile not found"
                )
        else:
            serializer.save()

class MentorAssignmentViewSet(viewsets.ModelViewSet):
    queryset = MentorAssignment.objects.all()
    serializer_class = MentorAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['mentor__user__username', 'batch__name']
    ordering_fields = ['assigned_date']
    
    def get_permissions(self):
        # Only admins can manage mentor assignments
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return [IsAuthenticated()]
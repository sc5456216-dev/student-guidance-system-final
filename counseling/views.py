
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsStudent, IsAdvisor, IsStaffOrAdmin
from .models import CounselingSession
from .serializers import CounselingSessionSerializer, CounselingSessionDetailSerializer


class CounselingSessionViewSet(viewsets.ModelViewSet):
    queryset = CounselingSession.objects.filter(is_deleted=False)
    serializer_class = CounselingSessionSerializer

    def get_permissions(self):
        # Only students can create (request) sessions
        if self.action == 'create':
            return [IsAuthenticated(), IsStudent()]
        # Only advisors or staff/admin can update or delete
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdvisor() | IsStaffOrAdmin()]
        # List and retrieve: any authenticated user
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CounselingSessionDetailSerializer
        return CounselingSessionSerializer
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'student':
            qs = qs.filter(student=user)
        elif user.role == 'advisor':
            qs = qs.filter(advisor=user)   
            return qs

  
    def perform_create(self, serializer):
        # Automatically set the student to the logged‑in user
        serializer.save(student=self.request.user)
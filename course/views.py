from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, BasePermission
from authentication.permissions import IsAdvisor
from .models import Course, CourseBatch
from .serializers import CourseSerializer, CourseBatchSerializer, CourseWithBatchesSerializer
from .permissions import IsStaffUser


# ---------- CUSTOM PERMISSION WITH DEBUG ----------
class IsAdminOrSuperuser(BasePermission):
    """
    Custom permission that allows superusers, staff, and admin users.
    Includes debug prints to help troubleshoot.
    """
    def has_permission(self, request, view):
        print("=" * 60)
        print("🔍 IsAdminOrSuperuser - Checking Permission")
        print(f"   User: {request.user}")
        print(f"   Is Authenticated: {request.user.is_authenticated if request.user else False}")
        print(f"   Is Staff: {request.user.is_staff if request.user else False}")
        print(f"   Is Superuser: {request.user.is_superuser if request.user else False}")
        print(f"   Method: {request.method}")
        print(f"   Action: {view.action if hasattr(view, 'action') else 'N/A'}")
        print("=" * 60)
        
        # Allow superuser unconditionally
        if request.user and request.user.is_superuser:
            print("✅ ALLOWED: Superuser")
            return True
        
        # Allow staff users
        if request.user and request.user.is_staff:
            print("✅ ALLOWED: Staff user")
            return True
        
        # For read-only methods, allow all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            if request.user and request.user.is_authenticated:
                print("✅ ALLOWED: Authenticated user (read-only)")
                return True
        
        print("❌ DENIED: No matching permission")
        return False


# ---------- COURSE VIEWSET ----------
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_deleted=False)
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'code']
    ordering_fields = ['title', 'fee', 'duration_weeks']

    def get_permissions(self):
        print("=" * 60)
        print("🔍 CourseViewSet.get_permissions() called")
        print(f"   Action: {self.action}")
        print(f"   Method: {self.request.method if hasattr(self, 'request') else 'N/A'}")
        print("=" * 60)
        
        # Option 1: Try with custom permission (recommended)
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminOrSuperuser()]
        
        # Option 2: TEMPORARY - Allow ANYONE (use this to test if permissions are the issue)
        # return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseWithBatchesSerializer
        return CourseSerializer

    def create(self, request, *args, **kwargs):
        print("=" * 60)
        print("🔍 CourseViewSet.create() called")
        print(f"   User: {request.user}")
        print(f"   Data: {request.data}")
        print("=" * 60)
        return super().create(request, *args, **kwargs)


# ---------- COURSE BATCH VIEWSET ----------
class CourseBatchViewSet(viewsets.ModelViewSet):
    queryset = CourseBatch.objects.filter(is_deleted=False)
    serializer_class = CourseBatchSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['batch_name', 'instructor']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrSuperuser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset
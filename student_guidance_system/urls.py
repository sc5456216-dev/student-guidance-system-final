from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# ---------- IMPORTANT: Import views from the same directory ----------
from . import views   # <-- This makes `views.home` available

# ---------- App Imports ----------
from authentication.views import RegisterView, LoginView, MeView, ProfileView
from course.views import CourseViewSet, CourseBatchViewSet
from appointments.views import AppointmentViewSet
from assessment.views import QuestionViewSet, AssessmentResultViewSet
from counseling.views import CounselingSessionViewSet
from enrollment.views import EnrollmentViewSet
from students.views import cache_test_view, StudentDashboardView, StudentProfileView
from students.views import test_email_view, dashboard_page
from notifications.views import NotificationSettingsView

# ---------- Router Configuration ----------
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'batches', CourseBatchViewSet, basename='batch')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'questions', QuestionViewSet, basename='questions')
router.register(r'assessments', AssessmentResultViewSet, basename='assessment-results')
router.register(r'counseling', CounselingSessionViewSet, basename='counseling')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

# ---------- URL Patterns ----------
urlpatterns = [
    # Home page – uses `views.home` from this directory
    path('', views.home, name='home'),

    # Django Admin
    path('admin/', admin.site.urls),

    # API endpoints (DRF router)
    path('api/', include(router.urls)),

    # Authentication endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', MeView.as_view(), name='me'),
    path('api/auth/profile/', ProfileView.as_view(), name='profile'),

    # API Documentation (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redis Cache Test Endpoint
    path('api/test-cache/', cache_page(60 * 15)(cache_test_view), name='cache_test'),

    # Student endpoints
    path('api/test-email/', test_email_view, name='test_email'),
    path('api/students/profile/', StudentProfileView.as_view(), name='student-profile'),
    path('api/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('dashboard/', dashboard_page, name='dashboard_page'),
    path('api/notification-settings/', NotificationSettingsView.as_view(), name='notification-settings'),

    # Admin dashboard (custom app)
    path('api/admin/', include('admin_dashboard.urls')),
]

# ---------- Media Files (Development Only) ----------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

   

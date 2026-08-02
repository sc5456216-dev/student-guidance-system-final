"""
URL configuration for student_guidance_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny
from django.views.decorators.cache import cache_page
from students.views import, cache_test_view, StudentDashboardView
from django.urls import include

# Authentication app imports
from authentication.views import RegisterView, LoginView, MeView, ProfileView

# Course app imports
from course.views import CourseViewSet, CourseBatchViewSet

# Appointments app imports
from appointments.views import AppointmentViewSet

# Assessment app imports
from assessment.views import QuestionViewSet, AssessmentResultViewSet

# Counseling app imports
from counseling.views import CounselingSessionViewSet

# Enrollment app imports
from enrollment.views import EnrollmentViewSet

# Students app imports (moved from .views to students.views)
from students.views import home, cache_test_view
from students.views import StudentProfileView 


# DRF Spectacular (API documentation)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from students.views import test_email_view
from students.views import dashboard_page 
from . import views   
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
    # Home page
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
    
    path('api/test-email/', test_email_view, name='test_email'),
    path('api/students/profile/', StudentProfileView.as_view(), name='student-profile'),
    path('api/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('dashboard/', dashboard_page, name='dashboard_page'),
    path('api/notification-settings/', NotificationSettingsView.as_view(), name='notification-settings'),
    path('api/admin/', include('admin_dashboard.urls')),
]

# ---------- Media Files (Development Only) ----------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


   

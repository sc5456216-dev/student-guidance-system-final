# appointments/views.py
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from authentication.permissions import IsStudent, IsStudentOrAdvisorOrStaffOrAdmin
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentDetailSerializer
from .permissions import IsAppointmentAccessible
from .paginations import AppointmentPagination
from students.utils import send_appointment_confirmation
from profiles.models import StudentProfile
from notifications.models import NotificationSettings  
import traceback
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.filter(is_deleted=False)
    serializer_class = AppointmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'notes']
    ordering_fields = ['scheduled_time', 'created_at']
    pagination_class = AppointmentPagination

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), IsStudentOrAdvisorOrStaffOrAdmin()]
        elif self.action == 'create':
            return [IsAuthenticated(), IsStudent()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAppointmentAccessible()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AppointmentDetailSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = queryset.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return queryset.none()
        elif user.role == 'advisor':
            queryset = queryset.filter(advisor__user=user)

        student_id = self.request.query_params.get('student_id')
        advisor_id = self.request.query_params.get('advisor_id')
        status_filter = self.request.query_params.get('status')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if advisor_id:
            queryset = queryset.filter(advisor_id=advisor_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        print(f"🔍 User: {user} (ID: {user.id}), Role: {user.role}")

        try:
            if user.role == 'student':
                try:
                    student_profile = StudentProfile.objects.get(user=user)
                    print(f"✅ Found StudentProfile: {student_profile} (ID: {student_profile.id})")
                except StudentProfile.DoesNotExist:
                    print(f"❌ No StudentProfile for user {user.id}")
                    raise ValidationError({"student": "Student profile not found."})
                appointment = serializer.save(student=student_profile)
            else:
                # For staff/advisor, require 'student' in the request
                if 'student' not in serializer.validated_data:
                    raise ValidationError({"student": "This field is required for staff/advisor."})
                appointment = serializer.save()
                if 'advisor' not in serializer.validated_data:
                    appointment.advisor = user
                    appointment.save()

            print(f"✅ Appointment saved with ID: {appointment.id}")

            # ---------- SEND EMAIL NOTIFICATION ----------
            try:
                # This function now checks the user's email_notifications setting internally
                send_appointment_confirmation(appointment.student, appointment)
                print(f"📧 Email sent to {appointment.student.user.email}")
            except Exception as e:
                print(f"⚠️ Email error: {e}")

            # ---------- SEND WEBSOCKET NOTIFICATION ----------
            try:
                student_user = appointment.student.user
                # Check if in-app notifications are enabled
                try:
                    settings_obj = student_user.notification_settings
                    in_app_enabled = settings_obj.in_app_notifications
                except NotificationSettings.DoesNotExist:
                    # If no settings, default to sending
                    in_app_enabled = True

                if in_app_enabled:
                    channel_layer = get_channel_layer()
                    group_name = f'user_{student_user.id}'
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            'type': 'send_notification',
                            'message': f'New appointment booked on {appointment.scheduled_time}',
                            'appointment_id': appointment.id,
                            'status': appointment.status,
                        }
                    )
                    print(f"📡 In-app notification sent to user {student_user.id} (group: {group_name})")
                else:
                    print(f"🔕 In-app notifications disabled for user {student_user.id}")

            except Exception as ws_error:
                # Don't break the appointment if WebSocket fails
                print(f"⚠️ WebSocket notification error: {ws_error}")

        except Exception as e:
            print("=" * 60)
            print("🔥 ERROR in perform_create:")
            traceback.print_exc()
            print("=" * 60)
            raise
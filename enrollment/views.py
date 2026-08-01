import traceback
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Enrollment
from .serializers import EnrollmentSerializer
from course.models import CourseBatch
from authentication.models import User
from students.models import Student  
from students.utils import send_enrollment_confirmation


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.filter(is_deleted=False)
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            print("=" * 60)
            print("Creating enrollment...")
            user = self.request.user
            print(f"User: {user} (ID: {user.id})")

            # Get student – use the logged-in user unless superuser specifies another
            student_id = self.request.data.get('student')
            if student_id and user.is_superuser:
                try:
                    student = User.objects.get(id=student_id)
                except User.DoesNotExist:
                    raise ValidationError({"student": "Student does not exist."})
            else:
                student = user

            # Get batch
            batch_id = self.request.data.get('batch')
            if not batch_id:
                raise ValidationError({"batch": "Batch is required."})
            try:
                batch = CourseBatch.objects.get(id=batch_id, is_deleted=False)
            except CourseBatch.DoesNotExist:
                raise ValidationError({"batch": "Batch not found."})

            # Save enrollment and get the instance
            enrollment = serializer.save(student=student, batch=batch)
            print("✅ Enrollment saved successfully.")

            # ---------- SEND ENROLLMENT CONFIRMATION EMAIL ----------
            try:
                # Get the Student profile for this user
                student_profile = Student.objects.get(user=student)
                send_enrollment_confirmation(student_profile, batch)
                print(f"📧 Enrollment confirmation email sent to {student.email}")
            except Student.DoesNotExist:
                print(f"⚠️ Student profile not found for {student.email}, skipping email.")
            except Exception as email_error:
                print(f"⚠️ Failed to send email: {email_error}")

        except Exception as e:
            print("=" * 60)
            print("🔥 ERROR in perform_create:")
            traceback.print_exc()
            print("=" * 60)
            raise

    # ✅ REMOVE the custom 'create' method entirely – let DRF handle errors
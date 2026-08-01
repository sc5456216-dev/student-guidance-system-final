from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch

from .models import Enrollment
from course.models import CourseBatch
from assessment.models import AssessmentResult
from authentication.models import User

User = get_user_model()


class EnrollmentModelTest(TestCase):
    """Test the Enrollment model constraints and methods."""

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            email='student@example.com',
            password='pass123',
            role='student'
        )
        cls.advisor = User.objects.create_user(
            email='advisor@example.com',
            password='pass123',
            role='advisor'
        )
        cls.batch = CourseBatch.objects.create(
            name='Python Batch 1',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            is_active=True
        )
        cls.assessment = AssessmentResult.objects.create(
            student=cls.student,
            batch=cls.batch,
            score=85.0
        )

    def test_create_enrollment(self):
        """Test basic enrollment creation."""
        enrollment = Enrollment.objects.create(
            student=self.student,
            batch=self.batch,
            assessment_result=self.assessment,
            payment_status='pending',
            status='pending'
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.batch, self.batch)
        self.assertEqual(enrollment.payment_status, 'pending')
        self.assertEqual(enrollment.status, 'pending')
        self.assertFalse(enrollment.is_deleted)  
        self.assertIsNotNone(enrollment.enrolled_at)

    def test_unique_active_enrollment(self):
        """Ensure duplicate active enrollments are rejected."""
        Enrollment.objects.create(
            student=self.student,
            batch=self.batch,
            assessment_result=self.assessment
        )
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                batch=self.batch,
                assessment_result=self.assessment
            )

    def test_soft_delete_allows_new_enrollment(self):
        """After soft-deleting an enrollment, a new one can be created."""
        enrollment = Enrollment.objects.create(
            student=self.student,
            batch=self.batch,
            assessment_result=self.assessment
        )
        enrollment.is_deleted = True
        enrollment.save()

        new_enrollment = Enrollment.objects.create(
            student=self.student,
            batch=self.batch,
            assessment_result=self.assessment
        )
        self.assertIsNotNone(new_enrollment.pk)

    def test_str_representation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            batch=self.batch,
            assessment_result=self.assessment
        )
        expected = f"{self.student.email} -> {self.batch}"
        self.assertEqual(str(enrollment), expected)


class EnrollmentSerializerTest(APITestCase):
    """Test the EnrollmentSerializer validation and read-only fields."""

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            email='student2@example.com',
            password='pass123',
            role='student'
        )
        cls.batch = CourseBatch.objects.create(
            name='Python Batch 2',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            is_active=True
        )
        cls.assessment = AssessmentResult.objects.create(
            student=cls.student,
            batch=cls.batch,
            score=90.0
        )
        cls.url = reverse('enrollment-list')  

    def test_create_enrollment_serializer_valid(self):
        """Test valid creation via serializer."""
        data = {
            'student': self.student.id,
            'batch': self.batch.id,
            'assessment_result': self.assessment.id,
            'payment_status': 'pending',
            'status': 'pending'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_duplicate_enrollment_validation(self):
        """Serializer should raise a validation error for duplicate active enrollment."""
        Enrollment.objects.create(
            student=self.student,
            batch=self.batch,
            assessment_result=self.assessment
        )
        data = {
            'student': self.student.id,
            'batch': self.batch.id,
            'assessment_result': self.assessment.id,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('already exists', str(response.data['non_field_errors']))

    def test_read_only_fields(self):
        """enrolled_at, id, created_at, updated_at should be read-only."""
        enrollment = Enrollment.objects.create(
            student=self.student,
            batch=self.batch,
            assessment_result=self.assessment
        )
        url = reverse('enrollment-detail', args=[enrollment.pk])
        data = {
            'enrolled_at': '2020-01-01T00:00:00Z',  
            'id': 999,
            'created_at': '2020-01-01T00:00:00Z',
            'updated_at': '2020-01-01T00:00:00Z',
            'student': self.student.id,
            'batch': self.batch.id,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        enrollment.refresh_from_db()
        # These fields should remain unchanged
        self.assertNotEqual(enrollment.enrolled_at, timezone.datetime(2020, 1, 1, tzinfo=timezone.utc))
        self.assertNotEqual(enrollment.id, 999)


class EnrollmentViewSetTest(APITestCase):
    """Test permissions, filtering, and soft-delete in the viewset."""

    @classmethod
    def setUpTestData(cls):
        cls.student1 = User.objects.create_user(
            email='student1@example.com',
            password='pass123',
            role='student'
        )
        cls.student2 = User.objects.create_user(
            email='student2@example.com',
            password='pass123',
            role='student'
        )
        cls.advisor = User.objects.create_user(
            email='advisor@example.com',
            password='pass123',
            role='advisor'
        )
        cls.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='pass123'
        )
        cls.batch1 = CourseBatch.objects.create(
            name='Batch A',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            is_active=True
        )
        cls.batch2 = CourseBatch.objects.create(
            name='Batch B',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            is_active=True
        )
        cls.enrollment1 = Enrollment.objects.create(
            student=cls.student1,
            batch=cls.batch1
        )
        cls.enrollment2 = Enrollment.objects.create(
            student=cls.student1,
            batch=cls.batch2
        )
        # One enrollment for student2
        cls.enrollment3 = Enrollment.objects.create(
            student=cls.student2,
            batch=cls.batch1
        )
        cls.list_url = reverse('enrollment-list')

    def test_student_sees_only_own_enrollments(self):
        """A student should only see their own enrollments."""
        self.client.force_authenticate(user=self.student1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # only his two enrollments
        ids = [enr['id'] for enr in response.data]
        self.assertIn(self.enrollment1.id, ids)
        self.assertIn(self.enrollment2.id, ids)
        self.assertNotIn(self.enrollment3.id, ids)

    def test_advisor_sees_all_enrollments(self):
        """Advisor/staff should see all active enrollments."""
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_student_can_create_enrollment(self):
        """A student can create an enrollment (POST)."""
        self.client.force_authenticate(user=self.student2)
        data = {
            'batch': self.batch2.id,
            'payment_status': 'pending',
            'status': 'pending'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student'], self.student2.id)

    def test_advisor_cannot_create_enrollment(self):
        """Advisor should not be allowed to create (only students)."""
        self.client.force_authenticate(user=self.advisor)
        data = {'batch': self.batch2.id}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_update_or_delete(self):
        """Student cannot update or delete any enrollment."""
        self.client.force_authenticate(user=self.student1)
        detail_url = reverse('enrollment-detail', args=[self.enrollment1.id])

       
        response = self.client.patch(detail_url, {'status': 'confirmed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # delete
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_advisor_can_update_and_delete(self):
        """Advisor can update and soft-delete an enrollment."""
        self.client.force_authenticate(user=self.advisor)
        detail_url = reverse('enrollment-detail', args=[self.enrollment1.id])

       
        response = self.client.patch(detail_url, {'status': 'confirmed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment1.refresh_from_db()
        self.assertEqual(self.enrollment1.status, 'confirmed')

        
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.enrollment1.refresh_from_db()
        self.assertTrue(self.enrollment1.is_deleted)

    def test_admin_can_update_and_delete(self):
        """Admin (superuser) can also update and delete."""
        self.client.force_authenticate(user=self.admin)
        detail_url = reverse('enrollment-detail', args=[self.enrollment2.id])

        response = self.client.patch(detail_url, {'payment_status': 'paid'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment2.refresh_from_db()
        self.assertEqual(self.enrollment2.payment_status, 'paid')

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.enrollment2.refresh_from_db()
        self.assertTrue(self.enrollment2.is_deleted)

    def test_soft_deleted_enrollments_not_in_list(self):
        """Soft-deleted enrollments should not appear in the list."""
        self.client.force_authenticate(user=self.advisor)
        # Delete one
        self.client.delete(reverse('enrollment-detail', args=[self.enrollment1.id]))
        response = self.client.get(self.list_url)
        ids = [enr['id'] for enr in response.data]
        self.assertNotIn(self.enrollment1.id, ids)
        self.assertIn(self.enrollment2.id, ids)


class EnrollmentDetailSerializerTest(APITestCase):
    """Test the detail serializer with nested representations."""

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            email='student3@example.com',
            password='pass123',
            role='student'
        )
        cls.batch = CourseBatch.objects.create(
            name='Detail Batch',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            is_active=True
        )
        cls.enrollment = Enrollment.objects.create(
            student=cls.student,
            batch=cls.batch
        )

    def test_detail_serializer_returns_nested(self):
        """The retrieve action should use EnrollmentDetailSerializer with nested fields."""
        self.client.force_authenticate(user=self.student)
        url = reverse('enrollment-detail', args=[self.enrollment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       
        self.assertIn('student', response.data)
        self.assertIn('batch', response.data)
       
        self.assertEqual(response.data['student']['email'], self.student.email)
        self.assertEqual(response.data['batch']['name'], self.batch.name)
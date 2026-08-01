from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=100)
    guardian_contact = models.CharField(max_length=15)

    def __str__(self):
        return f"Student: {self.user.get_full_name()}"

class MentorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)  
    max_students = models.PositiveIntegerField(default=10) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Mentor: {self.user.get_full_name()} - {self.specialization}"

class CounselorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='counselor_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=100)  
    license_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Counselor: {self.user.get_full_name()}"
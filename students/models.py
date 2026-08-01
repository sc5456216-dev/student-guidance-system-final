from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model



class Student(models.Model):
    """
    Student profile model that extends the built-in User model.
    All student-specific data goes here.
    """
    # ---------- Core Relationship ----------
    # One-to-one link to the User model (supports both default and custom User models)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='students_student',  # Enables user.student_profile reverse lookup
        primary_key=False,
    )

    # ---------- Personal Information (Synced from User via signals) ----------
    name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(blank=True, null=True)

    # ---------- Additional Student-Specific Fields ----------
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Student-specific identifiers
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    enrollment_date = models.DateField(auto_now_add=True)
    
    # ---------- Academic Information ----------
    # If you have a Courses app, you can add a ManyToManyField later:
    # enrolled_courses = models.ManyToManyField('courses.Course', blank=True, related_name='students')
    
    # ---------- Timestamps ----------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['name']
        indexes = [
            models.Index(fields=['student_id']),  # Faster lookups by student ID
            models.Index(fields=['name']),
        ]

    def __str__(self):
        """Human-readable representation of the Student."""
        return self.name or self.user.username

    def get_full_name(self):
        """Returns the student's full name (convenience method)."""
        return self.name
    
    def get_email(self):
        """Returns the student's email."""
        return self.email or self.user.email

  
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.user.username
        super().save(*args, **kwargs)
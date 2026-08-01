from django.db import models
from django.conf import settings
from profiles.models import MentorProfile, StudentProfile

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)  
    title = models.CharField(max_length=200) 
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.title}"

class Batch(models.Model):
    name = models.CharField(max_length=100)  
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='batches')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    # LINK 1: Mentor assigned to the entire batch (Primary Mentor)
    primary_mentor = models.ForeignKey(
        MentorProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='primary_batches'
    )

    def __str__(self):
        return f"{self.name} ({self.course.code})"

class BatchEnrollment(models.Model):
    """
    Links Students to Batches (Many-to-Many relationship with extra fields)
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'batch'], name='unique_student_batch_enrollment')
    ]

    def __str__(self):
        return f"{self.student.user.username} -> {self.batch.name}"

class MentorAssignment(models.Model):
    """
    CRUCIAL: Links Mentors to specific Batches (and indirectly to Courses & Students).
    This allows multiple mentors per batch (e.g., one for theory, one for lab).
    """
    mentor = models.ForeignKey(MentorProfile, on_delete=models.SET_NULL, null = True, blank = True, related_name='assigned_batches')
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, related_name='assigned_mentors')
    assigned_date = models.DateField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)  # If True, override the Batch.primary_mentor

    class Meta:
        unique_together = ('mentor', 'batch')  # A mentor can't be assigned twice to the same batch

    def __str__(self):
        return f"{self.mentor.user.get_full_name()} -> {self.batch.name} (Primary: {self.is_primary})"
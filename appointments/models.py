from django.db import models
from base.models import BaseModel
from course.models import Course
from profiles.models import StudentProfile, CounselorProfile

class Appointment(BaseModel):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    student = models.ForeignKey(
        StudentProfile,            # Only StudentProfiles can go here
        on_delete=models.CASCADE,
        related_name='appointments'
       
    )
    advisor = models.ForeignKey(
        CounselorProfile,          # Only CounselorProfiles can go here
        on_delete=models.CASCADE,
        related_name='appointments'
        
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.email} ↔ {self.advisor.user.email} @ {self.scheduled_time}"

    class Meta:
        ordering = ['scheduled_time']
        indexes = [
            models.Index(fields=['scheduled_time']),
            models.Index(fields=['status']),
            models.Index(fields=['student', 'scheduled_time']),
            models.Index(fields=['advisor', 'scheduled_time']),
        ]
from django.db import models
from base.models import BaseModel
from authentication.models import User
from assessment.models import AssessmentResult

class CounselingSession(BaseModel):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='counseling_sessions')
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'advisor'})
    assessment_result = models.ForeignKey(AssessmentResult, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.email} with {self.counselor.email} at {self.scheduled_time}"
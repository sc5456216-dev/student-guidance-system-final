from django.db import models
from base.models import BaseModel
from authentication.models import User
from course.models import Course

class Question(BaseModel):
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    related_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.text[:50]


class AssessmentResult(BaseModel):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    course_recommendations = models.ManyToManyField(Course, blank=True)
    score = models.FloatField(default=0.0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} - {self.score}"
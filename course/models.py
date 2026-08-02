
from django.db import models
from base.models import BaseModel

class Course(BaseModel):
    title = models.CharField(max_length=200, verbose_name="Name")
    name = models.CharField(max_length=200) 
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    duration_weeks = models.IntegerField(null=True, blank=True)
    fee = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # optional extra status

    def __str__(self):
         return self.name

    class Meta:
        ordering = ['name']  # override BaseModel's default if needed


class CourseBatch(BaseModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='batches'
    )
    batch_name = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    instructor = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.code} - {self.batch_name}"

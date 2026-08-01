from django.contrib import admin
from .models import Course, Batch, BatchEnrollment, MentorAssignment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'credits', 'is_active']
    search_fields = ['code', 'title']

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'start_date', 'end_date', 'is_active']
    search_fields = ['name', 'course__title']

@admin.register(BatchEnrollment)
class BatchEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'batch', 'enrolled_date', 'is_active']
    search_fields = ['student__user__username', 'batch__name']

@admin.register(MentorAssignment)
class MentorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['mentor', 'batch', 'assigned_date', 'is_primary']
    search_fields = ['mentor__user__username', 'batch__name']
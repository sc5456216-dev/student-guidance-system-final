from django.contrib import admin
from .models import StudentProfile, MentorProfile, CounselorProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'roll_number', 'phone_number', 'guardian_name']
    search_fields = ['user__username', 'user__email', 'roll_number']

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'specialization', 'is_active']
    search_fields = ['user__username', 'employee_id']

@admin.register(CounselorProfile)
class CounselorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'designation', 'is_active']
    search_fields = ['user__username', 'employee_id']
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'student_id', 'enrollment_date', 'created_at')
    search_fields = ('name', 'email', 'student_id')
    list_filter = ('enrollment_date',)
    readonly_fields = ('created_at', 'updated_at')
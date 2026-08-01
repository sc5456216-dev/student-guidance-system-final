
from django.contrib import admin
from .models import Course, CourseBatch

class CourseBatchInline(admin.TabularInline):
    model = CourseBatch
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'fee', 'is_active', 'is_deleted')
    list_filter = ('is_active', 'is_deleted')
    search_fields = ('code', 'title')
    inlines = [CourseBatchInline]

    def get_queryset(self, request):
        # Use all_objects to include soft-deleted courses
        return Course.all_objects.all()

@admin.register(CourseBatch)
class CourseBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_name', 'course', 'start_date', 'capacity', 'is_active')
    list_filter = ('course', 'is_active')

    def get_queryset(self, request):
        # Also show all batches (including deleted ones)
        return CourseBatch.all_objects.all()
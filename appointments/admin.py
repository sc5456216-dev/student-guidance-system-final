
from django.contrib import admin 
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # Columns shown in the list view
    list_display = (
        'id', 
        'student', 
        'advisor', 
        'scheduled_time', 
        'status', 
        'is_deleted'
    )
    
    # Sidebar filters (exactly like counseling)
    list_filter = ('status', 'is_deleted', 'scheduled_time')
    
    # Search box
    search_fields = ('student__email', 'student__username', 'advisor__email', 'notes')
    
    # Default ordering (latest first)
    ordering = ('-scheduled_time',)
    
    # Fields grouped in the edit form
    fieldsets = (
        ('Student & Advisor', {
            'fields': ('student', 'advisor')
        }),
        ('Appointment Details', {
            'fields': ('scheduled_time', 'status', 'notes')
        }),
        ('Course Link', {
            'fields': ('course',),
            'classes': ('collapse',)  # Collapsible section
        }),
        ('Soft Delete', {
            'fields': ('is_deleted',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Read-only fields (auto-populated)
    readonly_fields = ('created_at', 'updated_at')
    
    # Bulk actions (just like counseling)
    actions = ['mark_as_scheduled', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_scheduled(self, request, queryset):
        queryset.update(status='scheduled')
    mark_as_scheduled.short_description = "Mark selected appointments as Scheduled"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected appointments as Completed"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected appointments as Cancelled"
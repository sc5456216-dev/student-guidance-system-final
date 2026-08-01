
from django.contrib import admin
from .models import CounselingSession

@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    # List view columns
    list_display = (
        'id', 
        'student', 
        'counselor', 
        'scheduled_time', 
        'status', 
        'is_deleted'
    )
    
    # Right-side filters
    list_filter = ('status', 'is_deleted', 'scheduled_time')
    
    # Search fields (supports searching by related fields)
    search_fields = (
        'student__email', 
        'student__username', 
        'counselor__email', 
        'notes'
    )
    
    # Default ordering
    ordering = ('-scheduled_time',)
    raw_id_fields = ('student', 'counselor', 'assessment_result')
    
    # Grouping fields in the detail edit form
    fieldsets = (
        ('Student & Counselor', {
            'fields': ('student', 'counselor')
        }),
        ('Session Details', {
            'fields': ('scheduled_time', 'status', 'notes')
        }),
        ('Assessment Link', {
            'fields': ('assessment_result',),
            'classes': ('collapse',)  
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
    
    # Foreign key lookups (shows search box instead of dropdown)
    raw_id_fields = ('student', 'counselor', 'assessment_result')
    
    # Custom bulk actions
    actions = ['mark_as_scheduled', 'mark_as_ongoing', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_scheduled(self, request, queryset):
        queryset.update(status='scheduled')
    mark_as_scheduled.short_description = "Mark selected sessions as Scheduled"
    
    def mark_as_ongoing(self, request, queryset):
        queryset.update(status='ongoing')
    mark_as_ongoing.short_description = "Mark selected sessions as Ongoing"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected sessions as Completed"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected sessions as Cancelled"
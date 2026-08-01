from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Profile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'first_name', 'last_name', 'role')

# ---------- Profile Inline ----------
class ProfileInline(admin.TabularInline):
    model = Profile
    can_delete = False
    extra = 0
    fields = ('bio', 'image', 'address', 'birth_date')
    # ✅ Remove readonly_fields

# ---------- Custom User Admin ----------
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Extra Information', {'fields': ('role',)}),
        ('Soft Delete', {'fields': ('is_deleted',), 'classes': ('collapse',)}),
    )
    
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name', 
        'role', 'is_active', 'is_deleted', 'is_staff'
    )
    
    list_filter = (
        'role', 'is_active', 'is_deleted', 'is_staff', 'is_superuser'
    )
    
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    
    inlines = [ProfileInline]
    raw_id_fields = ('groups', 'user_permissions')
    readonly_fields = ('last_login', 'date_joined')  # ✅ Only fields that exist
    
    actions = ['make_active', 'make_inactive', 'make_staff', 'make_advisor', 'make_student']
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected users as Active"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected users as Inactive"
    
    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)
    make_staff.short_description = "Grant Staff status to selected users"
    
    def make_advisor(self, request, queryset):
        queryset.update(role='advisor')
    make_advisor.short_description = "Change role to Advisor for selected users"
    
    def make_student(self, request, queryset):
        queryset.update(role='student')
    make_student.short_description = "Change role to Student for selected users"

# ---------- Profile Admin (Standalone) ----------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'birth_date')
    list_filter = ('birth_date',)
    search_fields = ('user__email', 'user__username', 'address')
    # ✅ Remove readonly_fields

# ---------- Register User ----------
admin.site.register(User, CustomUserAdmin)
from rest_framework.permissions import BasePermission

class IsAppointmentAccessible(BasePermission):
    """
    Object-level permission for appointments.
    - Students: only their own.
    - Advisors: only ones assigned to them.
    - Staff/SuperAdmin: all.
    """
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'super_admin' or user.is_staff:
            return True
        if user.role == 'student':
            return obj.student == user
        if user.role == 'advisor':
            return obj.advisor == user
        return False
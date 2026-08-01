from rest_framework.permissions import BasePermission

class IsAppointmentAccessible(BasePermission):
    """
    Object-level permission to allow:
    - Student: only their own appointments
    - Advisor: only appointments where they are the advisor
    - Staff/SuperAdmin: all
    """
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'student':
            return obj.student == user
        elif user.role == 'advisor':
            return obj.advisor == user
        elif user.role in ['staff', 'super_admin']:
            return True
        return False
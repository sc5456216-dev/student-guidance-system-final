
from rest_framework import permissions

class IsStaffUser(permissions.BasePermission):
    """
    Custom permission to only allow staff users to edit/create courses.
    """
    def has_permission(self, request, view):
        # Allow GET requests (list/retrieve) for everyone authenticated
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Allow POST/PUT/DELETE only for staff users
        return request.user and request.user.is_staff
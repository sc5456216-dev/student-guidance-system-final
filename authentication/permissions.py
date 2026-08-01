from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsAdvisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'advisor'

class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['staff', 'super_admin']

class IsAdvisorOrStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['advisor', 'staff', 'super_admin']    

class IsStudentOrAdvisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['student', 'advisor', 'super_admin']

class IsStudentOrAdvisorOrStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (IsStudentOrAdvisor().has_permission(request, view) or IsStaffOrAdmin().has_permission(request, view))    
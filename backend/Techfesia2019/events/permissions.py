from rest_framework import permissions


class IsStaffUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        else:
            if request.user.is_staff or request.user.is_superuser:
                return True
            else:
                return False

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        else:
            if request.user.is_staff or request.user.is_superuser:
                return True
            else:
                return False

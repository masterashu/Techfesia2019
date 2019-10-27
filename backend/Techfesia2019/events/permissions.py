from rest_framework import permissions

class IsAuthenticatedOrGet(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.method == 'GET' or super().has_object_permission(request, view, obj)

    def has_permission(self, request, view):
        return request.method == 'GET' or super().has_permission(request, view)


class IsStaffUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        else:
            return False

    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        else:
            return False

class IsStaffUserOrGet(IsStaffUser):
    def has_object_permission(self, request, view, obj):
        return request.method == 'GET' or super().has_object_permission(request, view, obj)

    def has_permission(self, request, view):
        return request.method == 'GET' or super().has_permission(request, view)
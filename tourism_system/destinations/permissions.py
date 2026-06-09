from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """L'admin peut tout faire, les autres peuvent seulement lire"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """L'admin peut tout faire, les autres peuvent seulement lire"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """Le propriétaire peut modifier, l'admin peut tout faire"""
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False